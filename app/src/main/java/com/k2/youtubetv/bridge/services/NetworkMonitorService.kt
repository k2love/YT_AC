package com.k2.youtubetv.bridge.services

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.util.Log
import org.json.JSONObject

class NetworkMonitorService(private val context: Context) : CobaltService {

    companion object {
        private const val TAG = "NetworkMonitor"
        const val NAME = "com.google.youtube.tv.networkmonitor"
    }

    override val serviceName: String = NAME
    private var clientSender: ((String) -> Unit)? = null

    override fun onOpen(serviceId: Int, sender: (String) -> Unit) {
        Log.d(TAG, "Opening NetworkMonitorService ID: $serviceId")
        this.clientSender = sender
        sendNetworkStatus()
    }

    override fun onReceive(serviceId: Int, data: String) {
        sendNetworkStatus()
    }

    override fun onClose(serviceId: Int) {
        this.clientSender = null
    }

    private fun sendNetworkStatus() {
        try {
            val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager
            val net = cm?.activeNetwork
            val caps = cm?.getNetworkCapabilities(net)
            val downstreamKbps = caps?.linkDownstreamBandwidthKbps ?: 100000

            val resp = JSONObject().apply {
                put("network_bandwidth", downstreamKbps * 1000L)
            }
            clientSender?.invoke(resp.toString())
        } catch (e: Exception) {
            Log.e(TAG, "Error assembling network status", e)
        }
    }
}
