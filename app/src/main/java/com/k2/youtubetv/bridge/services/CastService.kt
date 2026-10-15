package com.k2.youtubetv.bridge.services

import android.os.Handler
import android.os.Looper
import android.util.Log
import android.webkit.WebView
import org.json.JSONObject

class CastService(
    private val webViewProvider: () -> WebView?
) : CobaltService {

    companion object {
        private const val TAG = "CastService"
        const val NAME = "com.google.android.gms.cast.tv"
    }

    override val serviceName: String = NAME
    private var clientSender: ((String) -> Unit)? = null
    private val mainHandler = Handler(Looper.getMainLooper())

    override fun onOpen(serviceId: Int, sender: (String) -> Unit) {
        Log.d(TAG, "Opening Cast Service ID: $serviceId")
        this.clientSender = sender
    }

    override fun onReceive(serviceId: Int, data: String) {
        Log.d(TAG, "Received Cast message: $data")
        try {
            val json = JSONObject(data)
            val what = json.optString("what")
            val message = json.optString("message")

            // Parse video ID from Cast payloads if incoming
            if (message.contains("videoId")) {
                val msgObj = JSONObject(message)
                val videoId = msgObj.optString("videoId")
                if (videoId.isNotEmpty()) {
                    Log.d(TAG, "Remote Cast request to play video: $videoId")
                    mainHandler.post {
                        val webView = webViewProvider()
                        webView?.loadUrl("https://www.youtube.com/tv?v=$videoId")
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error handling Cast message", e)
        }
    }

    override fun onClose(serviceId: Int) {
        Log.d(TAG, "Closing Cast Service ID: $serviceId")
        this.clientSender = null
    }
}
