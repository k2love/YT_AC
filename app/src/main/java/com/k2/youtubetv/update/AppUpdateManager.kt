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
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream
import java.util.concurrent.TimeUnit

class AppUpdateManager(private val activity: Activity) {

    companion object {
        private const val TAG = "AppUpdateManager"
        private const val GITHUB_REPO = "k2love/YT_AC"
        private const val GITHUB_API_URL = "https://api.github.com/repos/$GITHUB_REPO/releases/latest"
    }

    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    /**
     * GitHub 최신 릴리즈 정보를 비동기로 조회하고 업데이트가 있을 경우 안내 다이얼로그 표시
     */
    fun checkForUpdates(isManualCheck: Boolean = false) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val updateInfo = fetchLatestReleaseInfo()
                if (updateInfo != null && VersionComparator.isNewerVersion(updateInfo.tagName, BuildConfig.VERSION_NAME)) {
                    Log.i(TAG, "New update available: ${updateInfo.tagName} (Current: ${BuildConfig.VERSION_NAME})")
                    withContext(Dispatchers.Main) {
                        if (!activity.isFinishing && !activity.isDestroyed) {
                            showUpdateDialog(updateInfo)
                        }
                    }
                } else {
                    Log.d(TAG, "App is up to date (Current: ${BuildConfig.VERSION_NAME})")
                    if (isManualCheck) {
                        withContext(Dispatchers.Main) {
                            Toast.makeText(activity, "현재 최신 버전을 사용 중입니다. (${BuildConfig.VERSION_NAME})", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Failed to check for updates: ${e.message}")
                if (isManualCheck) {
                    withContext(Dispatchers.Main) {
                        Toast.makeText(activity, "업데이트 확인 중 오류가 발생했습니다.", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }
    }

    /**
     * GitHub API를 통해 최신 릴리즈 정보 파싱
     */
    private fun fetchLatestReleaseInfo(): UpdateInfo? {
        val request = Request.Builder()
            .url(GITHUB_API_URL)
            .header("Accept", "application/vnd.github.v3+json")
            .header("User-Agent", "YT_TV_AC-AndroidTV")
            .build()

        val response = httpClient.newCall(request).execute()
        if (!response.isSuccessful) {
            Log.w(TAG, "GitHub API returned code: ${response.code}")
            return null
        }

        val responseBody = response.body?.string() ?: return null
        val json = JSONObject(responseBody)

        val tagName = json.optString("tag_name", "")
        val title = json.optString("name", tagName)
        val body = json.optString("body", "")
        val htmlUrl = json.optString("html_url", "https://github.com/$GITHUB_REPO/releases")

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
            apkDownloadUrl = htmlUrl
        }

        val versionName = tagName.removePrefix("v").removePrefix("V")
        return UpdateInfo(
            tagName = tagName,
            versionName = versionName,
            title = title,
            changelog = body,
            downloadUrl = apkDownloadUrl,
            apkSize = apkSize
        )
    }

    /**
     * Android TV 맞춤형 업데이트 안내 다이얼로그 표시
     */
    private fun showUpdateDialog(updateInfo: UpdateInfo) {
        val displayChangelog = if (updateInfo.changelog.isNotBlank()) {
            val trimmed = updateInfo.changelog.lines().take(6).joinToString("\n")
            "\n\n[주요 변경사항]\n$trimmed"
        } else ""

        val message = "새로운 버전(${updateInfo.tagName})이 출시되었습니다.$displayChangelog\n\n지금 업데이트를 다운로드하여 설치하시겠습니까?"

        val dialog = AlertDialog.Builder(activity)
            .setTitle("YouTube TV 신규 업데이트 알림")
            .setMessage(message)
            .setPositiveButton("지금 업데이트") { _, _ ->
                startDownloadAndInstall(updateInfo)
            }
            .setNegativeButton("나중에") { dialog, _ ->
                dialog.dismiss()
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
    private fun startDownloadAndInstall(updateInfo: UpdateInfo) {
        if (!updateInfo.downloadUrl.endsWith(".apk", ignoreCase = true)) {
            // APK 직접 다운로드 링크가 아닐 경우 웹 브라우저로 이동
            openBrowserFallback(updateInfo.downloadUrl)
            return
        }

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
                    .url(updateInfo.downloadUrl)
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
                    // 미확인 앱 설치 권한 요청 안내
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
