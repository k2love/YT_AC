package com.k2.youtubetv.webview

import android.graphics.Bitmap
import android.util.Log
import android.view.View
import android.view.ViewGroup
import android.webkit.ConsoleMessage
import android.webkit.PermissionRequest
import android.webkit.WebChromeClient
import android.widget.FrameLayout

class TVWebChromeClient(
    private val customViewContainer: FrameLayout? = null,
    private val mainContentView: View? = null
) : WebChromeClient() {

    companion object {
        private const val TAG = "KabukiWeb"
    }

    private var customView: View? = null
    private var customViewCallback: CustomViewCallback? = null

    override fun getDefaultVideoPoster(): Bitmap? {
        // Return transparent 1x1 bitmap to eliminate Android WebView default black box & white play button
        return Bitmap.createBitmap(1, 1, Bitmap.Config.ARGB_8888)
    }

    override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
        if (consoleMessage != null) {
            val msg = "[Line ${consoleMessage.lineNumber()}] ${consoleMessage.message()}"
            when (consoleMessage.messageLevel()) {
                ConsoleMessage.MessageLevel.ERROR -> Log.e(TAG, msg)
                ConsoleMessage.MessageLevel.WARNING -> Log.w(TAG, msg)
                else -> Log.d(TAG, msg)
            }
        }
        return true
    }

    override fun onPermissionRequest(request: PermissionRequest?) {
        // Automatically grant audio/video/protected media permissions for TV playback
        request?.grant(request.resources)
    }

    override fun onShowCustomView(view: View?, callback: CustomViewCallback?) {
        if (customView != null) {
            callback?.onCustomViewHidden()
            return
        }

        customView = view
        customViewCallback = callback

        if (customViewContainer != null && view != null) {
            mainContentView?.visibility = View.GONE
            customViewContainer.addView(
                view,
                FrameLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.MATCH_PARENT
                )
            )
            customViewContainer.visibility = View.VISIBLE
        }
    }

    override fun onHideCustomView() {
        if (customView == null) return

        mainContentView?.visibility = View.VISIBLE
        customViewContainer?.visibility = View.GONE
        customViewContainer?.removeView(customView)
        customViewCallback?.onCustomViewHidden()

        customView = null
        customViewCallback = null
    }

    fun isCustomViewShowing(): Boolean = customView != null
}
