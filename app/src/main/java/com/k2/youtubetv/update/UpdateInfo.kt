package com.k2.youtubetv.update

/**
 * GitHub 릴리즈 정보를 담는 데이터 모델
 */
data class UpdateInfo(
    val tagName: String,
    val versionName: String,
    val title: String,
    val changelog: String,
    val downloadUrl: String,
    val apkSize: Long
)

object VersionComparator {
    /**
     * 원격 버전이 현재 버전보다 최신인지 비교 (Semantic Versioning 기반)
     * 예: v1.0.1 > 1.0.0 (true)
     */
    fun isNewerVersion(remote: String, current: String): Boolean {
        val cleanRemote = remote.trim().removePrefix("v").removePrefix("V")
        val cleanCurrent = current.trim().removePrefix("v").removePrefix("V")

        val remoteParts = parseVersionParts(cleanRemote)
        val currentParts = parseVersionParts(cleanCurrent)

        val maxLen = maxOf(remoteParts.size, currentParts.size)
        for (i in 0 until maxLen) {
            val r = remoteParts.getOrElse(i) { 0 }
            val c = currentParts.getOrElse(i) { 0 }
            if (r > c) return true
            if (r < c) return false
        }
        return false
    }

    private fun parseVersionParts(versionStr: String): List<Int> {
        return versionStr.split(".")
            .mapNotNull { part ->
                part.takeWhile { it.isDigit() }.toIntOrNull()
            }
    }
}
