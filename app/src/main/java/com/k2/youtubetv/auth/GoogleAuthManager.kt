package com.k2.youtubetv.auth

import android.accounts.Account
import android.accounts.AccountManager
import android.content.Context
import android.util.Log
import com.k2.youtubetv.bridge.services.SyncAuthCredentialService
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class GoogleAuthManager(
    private val context: Context,
    private val authService: SyncAuthCredentialService
) {
    companion object {
        private const val TAG = "GoogleAuthManager"
        private const val YOUTUBE_AUTH_SCOPE = "oauth2:https://www.googleapis.com/auth/youtube"
    }

    suspend fun syncDeviceGoogleAccountIfAvailable(): Boolean = withContext(Dispatchers.IO) {
        try {
            val accountManager = AccountManager.get(context)
            val accounts = accountManager.getAccountsByType("com.google")

            if (accounts.isEmpty()) {
                Log.d(TAG, "No device Google accounts found via AccountManager.")
                return@withContext false
            }

            val targetAccount: Account = accounts[0]
            Log.d(TAG, "Found device Google account: ${targetAccount.name}")

            // Attempt non-interactive token fetch
            val future = accountManager.getAuthToken(
                targetAccount,
                YOUTUBE_AUTH_SCOPE,
                null,
                false,
                null,
                null
            )

            val bundle = future.result
            val authToken = bundle.getString(AccountManager.KEY_AUTHTOKEN)

            if (!authToken.isNullOrEmpty()) {
                Log.d(TAG, "Obtained OAuth2 token for account: ${targetAccount.name}")
                // Save and notify frontend
                val prefs = context.getSharedPreferences("youtube_tv_auth", Context.MODE_PRIVATE)
                val expiry = System.currentTimeMillis() + (3600 * 1000) // Default 1 hour validity

                prefs.edit()
                    .putString("access_token", authToken)
                    .putLong("expiry", expiry)
                    .putString("owner_email", targetAccount.name)
                    .apply()

                authService.reportSavedCredentialIfValid()
                return@withContext true
            }
        } catch (e: Exception) {
            Log.w(TAG, "Device account auth token retrieval not permitted or failed: ${e.message}")
        }
        return@withContext false
    }
}
