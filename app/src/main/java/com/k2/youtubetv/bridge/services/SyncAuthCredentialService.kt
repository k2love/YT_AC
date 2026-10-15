package com.k2.youtubetv.bridge.services

import android.content.Context
import android.util.Log
import org.json.JSONObject

class SyncAuthCredentialService(private val context: Context) : CobaltService {

    companion object {
        private const val TAG = "SyncAuthCredential"
        const val NAME = "com.google.youtube.tv.syncauthcredential"
        private const val PREF_NAME = "youtube_tv_auth"
        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_EXPIRY = "expiry"
        private const val KEY_OWNER_EMAIL = "owner_email"
        private const val KEY_VISITOR_DATA = "visitor_data"
        private const val KEY_DATA_SYNC_ID = "data_sync_id"
    }

    override val serviceName: String = NAME
    private var clientSender: ((String) -> Unit)? = null
    private val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)

    override fun onOpen(serviceId: Int, sender: (String) -> Unit) {
        Log.d(TAG, "Opening SyncAuthCredentialService with ID: $serviceId")
        this.clientSender = sender
        reportSavedCredentialIfValid()
    }

    override fun onReceive(serviceId: Int, data: String) {
        Log.d(TAG, "SyncAuthCredential received data: $data")
        try {
            val root = JSONObject(data)
            val action = root.optString("action")
            if (action == "SyncAuthCredential") {
                val msg = root.optJSONObject("message")
                if (msg != null) {
                    val token = msg.optString("accessToken")
                    val expiry = msg.optLong("expiry")
                    val email = msg.optString("ownerAccountEmail")
                    val visitorData = msg.optString("activeVisitorData")
                    val dataSyncId = msg.optString("dataSyncId")

                    prefs.edit()
                        .putString(KEY_ACCESS_TOKEN, token)
                        .putLong(KEY_EXPIRY, expiry)
                        .putString(KEY_OWNER_EMAIL, email)
                        .putString(KEY_VISITOR_DATA, visitorData)
                        .putString(KEY_DATA_SYNC_ID, dataSyncId)
                        .apply()

                    Log.d(TAG, "Successfully synced and saved auth credentials for: $email (expiry: $expiry)")
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to parse SyncAuthCredential input payload", e)
        }
    }

    override fun onClose(serviceId: Int) {
        Log.d(TAG, "Closing SyncAuthCredentialService ID: $serviceId")
        this.clientSender = null
    }

    fun reportSavedCredentialIfValid() {
        val token = prefs.getString(KEY_ACCESS_TOKEN, null) ?: return
        val expiry = prefs.getLong(KEY_EXPIRY, 0L)
        val email = prefs.getString(KEY_OWNER_EMAIL, "") ?: ""

        val now = System.currentTimeMillis()
        if (now < expiry && token.isNotEmpty()) {
            val msgObj = JSONObject().apply {
                put("accessToken", token)
                put("expiry", expiry)
                put("ownerAccountEmail", email)
            }
            val reportObj = JSONObject().apply {
                put("action", "ReportAuthCredential")
                put("message", msgObj)
            }
            Log.d(TAG, "Reporting saved valid auth credential to Kabuki frontend: $email")
            clientSender?.invoke(reportObj.toString())
        } else {
            Log.d(TAG, "No valid non-expired auth credential to report.")
        }
    }
}
