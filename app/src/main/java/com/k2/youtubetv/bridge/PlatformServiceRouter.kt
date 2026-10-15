package com.k2.youtubetv.bridge

import android.content.Context
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.webkit.WebView
import com.k2.youtubetv.bridge.services.*
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger

class PlatformServiceRouter(
    private val context: Context,
    private val webViewProvider: () -> WebView?
) {
    companion object {
        private const val TAG = "PlatformServiceRouter"
    }

    private val mainHandler = Handler(Looper.getMainLooper())
    private val idCounter = AtomicInteger(1)
    private val servicesByName = ConcurrentHashMap<String, CobaltService>()
    private val activeSessions = ConcurrentHashMap<Int, CobaltService>()

    val syncAuthService = SyncAuthCredentialService(context)
    val recommendationsService = RecommendationsService(context)
    val networkMonitorService = NetworkMonitorService(context)
    val castService = CastService(webViewProvider)

    init {
        registerService(syncAuthService)
        registerService(recommendationsService)
        registerService(networkMonitorService)
        registerService(castService)
    }

    fun registerService(service: CobaltService) {
        servicesByName[service.serviceName] = service
        Log.d(TAG, "Registered platform service: ${service.serviceName}")
    }

    fun hasPlatformService(name: String): Boolean {
        return true // Report true to accept any expected Cobalt service
    }

    fun openService(name: String): Int {
        val serviceId = idCounter.getAndIncrement()
        val service = servicesByName[name] ?: object : CobaltService {
            override val serviceName: String = name
            private var clientSender: ((String) -> Unit)? = null
            override fun onOpen(serviceId: Int, sender: (String) -> Unit) {
                this.clientSender = sender
                Log.d(TAG, "[Stub] Opened fallback service: $name (ID: $serviceId)")
            }
            override fun onReceive(serviceId: Int, data: String) {
                Log.d(TAG, "[Stub] Received by $name: $data")
            }
            override fun onClose(serviceId: Int) {
                this.clientSender = null
            }
        }

        activeSessions[serviceId] = service
        service.onOpen(serviceId) { payload ->
            sendToClient(serviceId, payload)
        }
        return serviceId
    }

    fun sendToService(serviceId: Int, data: String) {
        val service = activeSessions[serviceId]
        if (service != null) {
            service.onReceive(serviceId, data)
        } else {
            Log.w(TAG, "sendToService for unknown serviceId: $serviceId")
        }
    }

    fun closeService(serviceId: Int) {
        val service = activeSessions.remove(serviceId)
        service?.onClose(serviceId)
    }

    private fun sendToClient(serviceId: Int, jsonPayload: String) {
        mainHandler.post {
            val webView = webViewProvider() ?: return@post
            val escapedPayload = jsonPayload
                .replace("\\", "\\\\")
                .replace("'", "\\'")
                .replace("\n", "\\n")
                .replace("\r", "\\r")

            val script = "window._onPlatformServiceReceive && window._onPlatformServiceReceive($serviceId, '$escapedPayload');"
            webView.evaluateJavascript(script, null)
        }
    }
}
