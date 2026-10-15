package com.k2.youtubetv.bridge.services

import android.content.ContentUris
import android.content.Context
import android.net.Uri
import android.util.Log
import androidx.tvprovider.media.tv.Channel
import androidx.tvprovider.media.tv.ChannelLogoUtils
import androidx.tvprovider.media.tv.PreviewProgram
import androidx.tvprovider.media.tv.TvContractCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import org.json.JSONArray
import org.json.JSONObject

class RecommendationsService(private val context: Context) : CobaltService {

    companion object {
        private const val TAG = "RecommendationsService"
        const val NAME = "com.google.youtube.tv.recommendations"
        private const val PREF_NAME = "youtube_tv_channels"
        private const val KEY_CHANNEL_ID = "main_channel_id"
    }

    override val serviceName: String = NAME
    private var clientSender: ((String) -> Unit)? = null
    private val scope = CoroutineScope(Dispatchers.IO)
    private val prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)

    override fun onOpen(serviceId: Int, sender: (String) -> Unit) {
        Log.d(TAG, "Opening RecommendationsService ID: $serviceId")
        this.clientSender = sender
        ensureChannelExists()
    }

    override fun onReceive(serviceId: Int, data: String) {
        Log.d(TAG, "Received recommendations data: $data")
        try {
            val root = JSONObject(data)
            val command = root.optString("command")
            if (command == "getPartnerId") {
                val resp = JSONObject().apply {
                    put("partner_id", "youtube_tv_clone")
                }
                clientSender?.invoke(resp.toString())
            } else if (command == "recommend") {
                val shelfParam = root.optString("shelfParam")
                val topic = root.optString("topic")
                val items = root.optJSONArray("items")

                if (items != null && items.length() > 0) {
                    scope.launch {
                        publishRecommendationsToLauncher(items)
                    }
                }

                val resp = JSONObject().apply {
                    put("response_code", 200)
                }
                clientSender?.invoke(resp.toString())
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error processing recommendation command", e)
        }
    }

    override fun onClose(serviceId: Int) {
        Log.d(TAG, "Closing RecommendationsService ID: $serviceId")
        this.clientSender = null
    }

    private fun ensureChannelExists(): Long {
        var channelId = prefs.getLong(KEY_CHANNEL_ID, -1L)
        if (channelId != -1L) {
            return channelId
        }

        try {
            val builder = Channel.Builder()
                .setType(TvContractCompat.Channels.TYPE_PREVIEW)
                .setDisplayName("YouTube 맞춤 동영상")
                .setDescription("내 취향에 맞는 추천 동영상")
                .setAppLinkIntentUri(Uri.parse("https://www.youtube.com/tv"))

            val channelUri = context.contentResolver.insert(
                TvContractCompat.Channels.CONTENT_URI,
                builder.build().toContentValues()
            )

            if (channelUri != null) {
                channelId = ContentUris.parseId(channelUri)
                prefs.edit().putLong(KEY_CHANNEL_ID, channelId).apply()
                TvContractCompat.requestChannelBrowsable(context, channelId)
                Log.d(TAG, "Created Android TV Launcher Channel with ID: $channelId")
            }
        } catch (e: Exception) {
            Log.w(TAG, "Could not register Android TV launcher channel (may not be Android TV device): ${e.message}")
        }
        return channelId
    }

    private fun publishRecommendationsToLauncher(items: JSONArray) {
        val channelId = ensureChannelExists()
        if (channelId <= 0) return

        try {
            // Clear existing programs
            context.contentResolver.delete(
                TvContractCompat.buildPreviewProgramsUriForChannel(channelId),
                null,
                null
            )

            val maxCount = minOf(items.length(), 10)
            for (i in 0 until maxCount) {
                val item = items.optJSONObject(i) ?: continue
                val videoId = item.optString("videoId")
                val title = item.optString("title", "YouTube Video")
                val desc = item.optString("description", "")
                val posterUrl = item.optString("thumbnailUrl")

                val program = PreviewProgram.Builder()
                    .setChannelId(channelId)
                    .setTitle(title)
                    .setDescription(desc)
                    .setPosterArtUri(if (posterUrl.isNotEmpty()) Uri.parse(posterUrl) else null)
                    .setIntentUri(Uri.parse("https://www.youtube.com/tv?v=$videoId"))
                    .setType(TvContractCompat.PreviewPrograms.TYPE_CLIP)
                    .build()

                context.contentResolver.insert(
                    TvContractCompat.PreviewPrograms.CONTENT_URI,
                    program.toContentValues()
                )
            }
            Log.d(TAG, "Published $maxCount recommendations to Android TV Home Channel ID $channelId")
        } catch (e: Exception) {
            Log.w(TAG, "Failed to update preview programs on launcher: ${e.message}")
        }
    }
}
