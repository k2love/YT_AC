package com.k2.youtubetv.bridge

import android.os.Build
import android.util.Log
import android.webkit.JavascriptInterface

class CobaltJsBridge(
    private val router: PlatformServiceRouter
) {
    companion object {
        const val INTERFACE_NAME = "NativeBridge"
        private const val TAG = "CobaltJsBridge"
    }

    @JavascriptInterface
    fun getBuildFingerprint(): String {
        return Build.FINGERPRINT.ifEmpty {
            "google/chromecast/eureka:12/STTE.231215.005/11324838:user/release-keys"
        }
    }

    @JavascriptInterface
    fun getChipset(): String {
        return Build.HARDWARE.ifEmpty { "Amlogic S905X4" }
    }

    @JavascriptInterface
    fun storageClear() {
        Log.d(TAG, "storageClear called from Web")
    }

    @JavascriptInterface
    fun storageFlush() {
        Log.d(TAG, "storageFlush called from Web")
    }

    @JavascriptInterface
    fun hasPlatformService(name: String): Boolean {
        return router.hasPlatformService(name)
    }

    @JavascriptInterface
    fun openPlatformService(name: String): Int {
        Log.d(TAG, "openPlatformService: $name")
        return router.openService(name)
    }

    @JavascriptInterface
    fun sendPlatformService(serviceId: Int, data: String) {
        router.sendToService(serviceId, data)
    }

    @JavascriptInterface
    fun closePlatformService(serviceId: Int) {
        Log.d(TAG, "closePlatformService: $serviceId")
        router.closeService(serviceId)
    }
}
