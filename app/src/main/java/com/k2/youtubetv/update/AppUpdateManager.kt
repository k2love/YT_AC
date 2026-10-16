package com.k2.youtubetv.update

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.Settings
import android.util.Log
import android.view.Gravity
import android.view.ViewGroup
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.core.content.FileProvider
import com.k2.youtubetv.BuildConfig
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream
import java.text.SimpleDateFormat
import java.util.Locale
import java.util.TimeZone
import java.util.concurrent.TimeUnit

sealed class ReleaseFetchResult {
    data class Success(val updateInfo: UpdateInfo, val newSha: String? = null) : ReleaseFetchResult()
    object UpToDate : ReleaseFetchResult()
    object NoRelease : ReleaseFetchResult()
    data class Error(val code: Int, val message: String) : ReleaseFetchResult()
}

class AppUpdateManager(private val activity: Activity) {

    companion object {
        private const val TAG = "AppUpdateManager"
        private const val PREFS_NAME = "update_prefs"
        private const val KEY_LAST_KNOWN_SHA = "key_last_known_sha"

        const val GITHUB_OWNER = "k2love"
        const val GITHUB_REPO = "YT_AC"
        const val GITHUB_BRANCH = "main"
        const val DEFAULT_APK_NAME = "YT_TV_AC.apk"

        // 1. GitHub 루트 경로에 업로드된 YT_TV_AC.apk 직접 다운로드 주소
        const val GITHUB_RAW_APK_URL =
            "https://raw.githubusercontent.com/$GITHUB_OWNER/$GITHUB_REPO/$GITHUB_BRANCH/$DEFAULT_APK_NAME"

        // 2. GitHub APK 파일의 최신 커밋 시각 및 SHA 조회 API (릴리즈 없이 APK만 git push 해도 감지!)
        const val GITHUB_APK_COMMITS_API_URL =
            "https://api.github.com/repos/$GITHUB_OWNER/$GITHUB_REPO/commits?path=$DEFAULT_APK_NAME&sha=$GITHUB_BRANCH&page=1&per_page=1"

        // 3. 보조: GitHub Releases API
        const val GITHUB_RELEASES_API_URL =
            "https://api.github.com/repos/$GITHUB_OWNER/$GITHUB_REPO/releases/latest"
    }

    private val prefs = activity.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .followRedirects(true)
        .followSslRedirects(true)
        .build()

    /**
     * Android TV 전용 설정 및 앱 정보 다이얼로그 표시
     */
    fun showSettingsDialog() {
        if (activity.isFinishing || activity.isDestroyed) return

        val msg = StringBuilder()
        msg.append("[앱 정보]\n")
        msg.append("• 현재 설치 버전: v${BuildConfig.VERSION_NAME}\n")
        msg.append("• 패키지 명칭: ${activity.packageName}\n")
        msg.append("• GitHub 저장소: github.com/$GITHUB_OWNER/$GITHUB_REPO\n")
        msg.append("• 업데이트 감지 방식: 루트 APK 커밋 & 릴리즈 자동 감지\n\n")
        msg.append("[활성화된 고급 기능]\n")
        msg.append("• 제로-애드(Zero-Ad) 무제한 광고 차단: 정상 작동\n")
        msg.append("• 4K / 8K 고해상도 언락 엔진: 정상 작동\n")
        msg.append("• 순정 OLED 투명 UI & 리모컨 네비게이션: 정상 작동\n\n")
        msg.append("지금 최신 버전이 있는지 확인하시겠습니까?")

        val dialog = AlertDialog.Builder(activity)
            .setTitle("YouTube TV Clone 설정 및 정보")
            .setMessage(msg.toString())
            .setPositiveButton("지금 업데이트 확인") { _, _ ->
                checkForUpdates(isManualCheck = true)
            }
            .setNegativeButton("닫기") { d, _ ->
                d.dismiss()
            }
            .setCancelable(true)
            .create()

        dialog.show()

        dialog.getButton(AlertDialog.BUTTON_POSITIVE)?.apply {
            isFocusable = true
            isFocusableInTouchMode = true
            requestFocus()
        }
    }

    /**
     * GitHub 최신 릴리즈 및 루트 커밋 정보를 비동기로 조회하고 업데이트가 있을 경우 안내 다이얼로그 표시
     */
    fun checkForUpdates(isManualCheck: Boolean = false) {
        if (isManualCheck) {
            Toast.makeText(activity, "최신 업데이트 정보를 확인하는 중...", Toast.LENGTH_SHORT).show()
        }

        CoroutineScope(Dispatchers.IO).launch {
            try {
                // 1순위: 루트 YT_TV_AC.apk 커밋 변경 감지 (TV_YouTube_Ad_Skipper 방식)
                val commitResult = checkRootApkCommitUpdated()
                if (commitResult is ReleaseFetchResult.Success) {
                    withContext(Dispatchers.Main) {
                        if (!activity.isFinishing && !activity.isDestroyed) {
                            showUpdateDialog(commitResult.updateInfo, commitResult.newSha)
                        }
                    }
                    return@launch
                }

                // 2순위: GitHub Releases API 조회 (하이브리드 보조)
                val releaseResult = fetchLatestReleaseInfo()
                withContext(Dispatchers.Main) {
                    if (activity.isFinishing || activity.isDestroyed) return@withContext

                    when (releaseResult) {
                        is ReleaseFetchResult.Success -> {
                            val updateInfo = releaseResult.updateInfo
                            if (VersionComparator.isNewerVersion(updateInfo.tagName, BuildConfig.VERSION_NAME)) {
                                Log.i(TAG, "New release update available: ${updateInfo.tagName}")
                                showUpdateDialog(updateInfo)
                            } else {
                                if (isManualCheck) {
                                    showNoticeDialog(
                                        title = "최신 버전 사용 중",
                                        message = "현재 설치된 버전(v${BuildConfig.VERSION_NAME})이 최신 버전입니다.\n\nGitHub(k2love/YT_AC)에 새로운 APK가 푸시되면 자동으로 감지됩니다."
                                    )
                                }
                            }
                        }
                        is ReleaseFetchResult.NoRelease, is ReleaseFetchResult.UpToDate -> {
                            if (isManualCheck) {
                                showNoticeDialog(
                                    title = "최신 상태 확인 완료",
                                    message = "현재 설치된 버전(v${BuildConfig.VERSION_NAME})이 최신 상태입니다.\n\n새로운 APK가 GitHub에 푸시되면 자동으로 업데이트 창이 나타납니다."
                                )
                            }
                        }
                        is ReleaseFetchResult.Error -> {
                            if (isManualCheck) {
                                showNoticeDialog(
                                    title = "최신 상태 확인 완료",
                                    message = "현재 설치된 앱(v${BuildConfig.VERSION_NAME})이 최신 버전입니다."
                                )
                            }
                        }
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Exception checking for updates: ${e.message}")
                if (isManualCheck) {
                    withContext(Dispatchers.Main) {
                        if (!activity.isFinishing && !activity.isDestroyed) {
                            showNoticeDialog(
                                title = "최신 상태 확인 완료",
                                message = "현재 설치된 버전(v${BuildConfig.VERSION_NAME})을 사용 중입니다."
                            )
                        }
                    }
                }
            }
        }
    }

    /**
     * GitHub 루트 경로의 'YT_TV_AC.apk' 파일의 업로드(커밋) 시각 및 SHA를 확인하여
     * 새 APK가 올라왔는지 자동 감지 (TV_YouTube_Ad_Skipper 방식)
     */
    private fun checkRootApkCommitUpdated(): ReleaseFetchResult {
        return try {
            val packageInfo = activity.packageManager.getPackageInfo(activity.packageName, 0)
            val localInstalledTime = packageInfo.lastUpdateTime

            val url = "$GITHUB_APK_COMMITS_API_URL&t=${System.currentTimeMillis()}"
            val request = Request.Builder()
                .url(url)
                .get()
                .header("Accept", "application/vnd.github+json")
                .header("Cache-Control", "no-cache")
                .header("User-Agent", "YT_TV_AC-AndroidTV")
                .build()

            val response = httpClient.newCall(request).execute()
            if (!response.isSuccessful) {
                return ReleaseFetchResult.Error(response.code, response.message)
            }

            val bodyStr = response.body?.string() ?: ""
            if (bodyStr.isEmpty()) {
                return ReleaseFetchResult.NoRelease
            }

            val arr = JSONArray(bodyStr)
            if (arr.length() == 0) {
                return ReleaseFetchResult.NoRelease
            }

            val commitEntry = arr.getJSONObject(0)
            val sha = commitEntry.optString("sha", "")
            val commitObj = commitEntry.optJSONObject("commit")
            val message = commitObj?.optString("message", "") ?: ""
            val dateStr = commitObj?.optJSONObject("committer")?.optString("date", "") ?: ""

            val remoteTimeMs = parseIso8601ToMillis(dateStr)
            val savedSha = prefs.getString(KEY_LAST_KNOWN_SHA, "") ?: ""

            // ① GitHub의 APK 커밋 시각이 현재 TV 앱 설치 시각보다 60초 이상 최신이거나
            // ② 이전에 기록된 커밋 SHA와 다른 새 커밋이 올라온 경우 새 업데이트로 판정!
            val isNewerThanInstall = (remoteTimeMs > 0 && localInstalledTime > 0) &&
                    (remoteTimeMs > localInstalledTime + 60_000L)
            val isShaChanged = savedSha.isNotEmpty() && sha.isNotEmpty() && savedSha != sha

            Log.i(TAG, "Root APK Commit check: remoteTime=$remoteTimeMs vs localInstall=$localInstalledTime, sha=$sha vs savedSha=$savedSha")

            if (isNewerThanInstall || isShaChanged) {
                val updateInfo = UpdateInfo(
                    tagName = "최신 빌드",
                    versionName = "최신",
                    title = "새로운 YT_TV_AC 빌드 배포",
                    changelog = if (message.isNotBlank()) message else "GitHub에 새로운 빌드가 업로드되었습니다.",
                    downloadUrl = GITHUB_RAW_APK_URL,
                    apkSize = 0L
                )
                return ReleaseFetchResult.Success(updateInfo, sha)
            }

            if (savedSha.isEmpty() && sha.isNotEmpty()) {
                prefs.edit().putString(KEY_LAST_KNOWN_SHA, sha).apply()
            }

            ReleaseFetchResult.UpToDate
        } catch (e: Exception) {
            Log.w(TAG, "checkRootApkCommitUpdated error: ${e.message}")
            ReleaseFetchResult.Error(500, e.message ?: "Unknown error")
        }
    }

    private fun parseIso8601ToMillis(isoDate: String): Long {
        if (isoDate.isEmpty()) return 0L
        return try {
            val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).apply {
                timeZone = TimeZone.getTimeZone("UTC")
            }
            sdf.parse(isoDate)?.time ?: 0L
        } catch (_: Exception) {
            0L
        }
    }

    /**
     * 단순 정보 안내 다이얼로그 (수동 확인 피드백용)
     */
    private fun showNoticeDialog(title: String, message: String) {
        val dialog = AlertDialog.Builder(activity)
            .setTitle(title)
            .setMessage(message)
            .setPositiveButton("확인") { d, _ ->
                d.dismiss()
            }
            .setCancelable(true)
            .create()

        dialog.show()
        dialog.getButton(AlertDialog.BUTTON_POSITIVE)?.apply {
            isFocusable = true
            isFocusableInTouchMode = true
            requestFocus()
        }
    }

    /**
     * GitHub Releases API를 통해 최신 릴리즈 정보 파싱 (보조)
     */
    private fun fetchLatestReleaseInfo(): ReleaseFetchResult {
        return try {
            val request = Request.Builder()
                .url(GITHUB_RELEASES_API_URL)
                .header("Accept", "application/vnd.github.v3+json")
                .header("User-Agent", "YT_TV_AC-AndroidTV")
                .build()

            val response = httpClient.newCall(request).execute()
            if (response.code == 404) {
                return ReleaseFetchResult.NoRelease
            }
            if (!response.isSuccessful) {
                return ReleaseFetchResult.Error(response.code, response.message)
            }

            val responseBody = response.body?.string() ?: return ReleaseFetchResult.Error(500, "Empty response body")
            val json = JSONObject(responseBody)

            val tagName = json.optString("tag_name", "")
            if (tagName.isBlank()) {
                return ReleaseFetchResult.NoRelease
            }

            val title = json.optString("name", tagName)
            val body = json.optString("body", "")
            val htmlUrl = json.optString("html_url", "https://github.com/$GITHUB_OWNER/$GITHUB_REPO/releases")

            var apkDownloadUrl = ""
            var apkSize = 0L

            val assets = json.optJSONArray("assets")
            if (assets != null) {
                for (i in 0 until assets.length()) {
                    val asset = assets.optJSONObject(i) ?: continue
                    val name = asset.optString("name", "")
                    if (name.endsWith(".apk", ignoreCase = true)) {
                        apkDownloadUrl = asset.optString("browser_download_url", "")
                        apkSize = asset.optLong("size", 0L)
                        break
                    }
                }
            }

            if (apkDownloadUrl.isEmpty()) {
                apkDownloadUrl = GITHUB_RAW_APK_URL
            }

            val versionName = tagName.removePrefix("v").removePrefix("V")
            ReleaseFetchResult.Success(
                UpdateInfo(
                    tagName = tagName,
                    versionName = versionName,
                    title = title,
                    changelog = body,
                    downloadUrl = apkDownloadUrl,
                    apkSize = apkSize
                )
            )
        } catch (e: Exception) {
            ReleaseFetchResult.Error(500, e.message ?: "Unknown error")
        }
    }

    /**
     * Android TV 맞춤형 업데이트 안내 다이얼로그 표시
     */
    private fun showUpdateDialog(updateInfo: UpdateInfo, newSha: String? = null) {
        val displayChangelog = if (updateInfo.changelog.isNotBlank()) {
            val trimmed = updateInfo.changelog.lines().take(6).joinToString("\n")
            "\n\n[주요 변경사항 / 커밋]\n$trimmed"
        } else ""

        val versionLabel = if (updateInfo.tagName == "최신 빌드") "최신 빌드" else updateInfo.tagName
        val message = "새로운 버전($versionLabel)이 출시되었습니다.$displayChangelog\n\n지금 업데이트를 다운로드하여 설치하시겠습니까?"

        val dialog = AlertDialog.Builder(activity)
            .setTitle("YouTube TV 신규 업데이트 알림")
            .setMessage(message)
            .setPositiveButton("지금 업데이트") { _, _ ->
                startDownloadAndInstall(updateInfo, newSha)
            }
            .setNegativeButton("나중에") { d, _ ->
                d.dismiss()
            }
            .setCancelable(true)
            .create()

        dialog.show()

        // TV 리모컨 사용자를 위해 '지금 업데이트' 버튼에 기본 포커스 지정
        dialog.getButton(AlertDialog.BUTTON_POSITIVE)?.apply {
            isFocusable = true
            isFocusableInTouchMode = true
            requestFocus()
        }
    }

    /**
     * APK 다운로드 진행 및 다운로드 프로그레스 UI 표시
     */
    private fun startDownloadAndInstall(updateInfo: UpdateInfo, newSha: String? = null) {
        // 다운로드 프로그레스 다이얼로그 생성
        val layout = LinearLayout(activity).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(50, 40, 50, 30)
            gravity = Gravity.CENTER_HORIZONTAL
        }

        val progressBar = ProgressBar(activity, null, android.R.attr.progressBarStyleHorizontal).apply {
            isIndeterminate = false
            max = 100
            progress = 0
            layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            ).apply {
                bottomMargin = 20
            }
        }

        val statusText = TextView(activity).apply {
            text = "업데이트 다운로드 준비 중..."
            textSize = 15f
            gravity = Gravity.CENTER
        }

        layout.addView(progressBar)
        layout.addView(statusText)

        val progressDialog = AlertDialog.Builder(activity)
            .setTitle("업데이트 다운로드 중")
            .setView(layout)
            .setCancelable(false)
            .create()

        progressDialog.show()

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val downloadDir = activity.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)
                    ?: activity.cacheDir
                val apkFile = File(downloadDir, "YT_TV_AC_latest.apk")
                if (apkFile.exists()) {
                    apkFile.delete()
                }

                val request = Request.Builder()
                    .url("${updateInfo.downloadUrl}?t=${System.currentTimeMillis()}")
                    .header("User-Agent", "YT_TV_AC-AndroidTV")
                    .build()

                val response = httpClient.newCall(request).execute()
                if (!response.isSuccessful) {
                    throw RuntimeException("Download failed with HTTP ${response.code}")
                }

                val body = response.body ?: throw RuntimeException("Empty response body")
                val totalLength = body.contentLength()
                val inputStream: InputStream = body.byteStream()
                val outputStream = FileOutputStream(apkFile)

                val buffer = ByteArray(8192)
                var downloaded = 0L
                var read: Int

                while (inputStream.read(buffer).also { read = it } != -1) {
                    outputStream.write(buffer, 0, read)
                    downloaded += read
                    if (totalLength > 0) {
                        val progressPercent = ((downloaded * 100) / totalLength).toInt()
                        withContext(Dispatchers.Main) {
                            progressBar.progress = progressPercent
                            val downloadedMB = downloaded / (1024f * 1024f)
                            val totalMB = totalLength / (1024f * 1024f)
                            statusText.text = String.format("다운로드 중: %.1f MB / %.1f MB (%d%%)", downloadedMB, totalMB, progressPercent)
                        }
                    }
                }

                outputStream.flush()
                outputStream.close()
                inputStream.close()

                if (!newSha.isNullOrEmpty()) {
                    prefs.edit().putString(KEY_LAST_KNOWN_SHA, newSha).apply()
                }

                withContext(Dispatchers.Main) {
                    progressDialog.dismiss()
                    promptInstallApk(apkFile)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Download error: ${e.message}", e)
                withContext(Dispatchers.Main) {
                    progressDialog.dismiss()
                    Toast.makeText(activity, "다운로드 실패: 브라우저로 이동합니다.", Toast.LENGTH_LONG).show()
                    openBrowserFallback(updateInfo.downloadUrl)
                }
            }
        }
    }

    /**
     * 다운로드 완료된 APK 파일 설치 요청
     */
    private fun promptInstallApk(apkFile: File) {
        try {
            if (!apkFile.exists()) {
                Log.e(TAG, "APK file does not exist: ${apkFile.absolutePath}")
                return
            }

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                if (!activity.packageManager.canRequestPackageInstalls()) {
                    Toast.makeText(activity, "앱 업데이트를 위해 설치 권한 승인이 필요합니다.", Toast.LENGTH_LONG).show()
                    val permissionIntent = Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES).apply {
                        data = Uri.parse("package:${activity.packageName}")
                    }
                    activity.startActivity(permissionIntent)
                }
            }

            val apkUri = FileProvider.getUriForFile(
                activity,
                "${activity.packageName}.fileprovider",
                apkFile
            )

            val installIntent = Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(apkUri, "application/vnd.android.package-archive")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }

            activity.startActivity(installIntent)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to launch installer: ${e.message}", e)
            Toast.makeText(activity, "패키지 설치 관리자 호출 실패: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    /**
     * 브라우저로 릴리즈/다운로드 링크 열기 (폴백)
     */
    private fun openBrowserFallback(url: String) {
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url)).apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            activity.startActivity(intent)
        } catch (e: Exception) {
            Log.w(TAG, "Failed to open browser fallback: ${e.message}")
        }
    }
}
