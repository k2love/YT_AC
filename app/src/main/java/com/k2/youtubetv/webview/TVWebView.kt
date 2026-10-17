package com.k2.youtubetv.webview

import android.annotation.SuppressLint
import android.content.Context
import android.util.AttributeSet
import android.util.Log
import android.view.KeyEvent
import android.view.View
import android.webkit.CookieManager
import android.webkit.WebSettings
import android.webkit.WebView
import androidx.webkit.WebViewCompat
import androidx.webkit.WebViewFeature
import com.k2.youtubetv.BuildConfig

class TVWebView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : WebView(context, attrs, defStyleAttr) {

    companion object {
        private const val TAG = "TVWebView"
        const val COBALT_USER_AGENT =
            "Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36"
    }

    init {
        // Remote DOM inspection via chrome://inspect / CDP.
        WebView.setWebContentsDebuggingEnabled(true)
        initTVWebSettings()
        setupDocumentStartScript()
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun initTVWebSettings() {
        setLayerType(View.LAYER_TYPE_HARDWARE, null)
        setBackgroundColor(0xFF000000.toInt())

        isFocusable = true
        isFocusableInTouchMode = true
        requestFocus()

        settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            mediaPlaybackRequiresUserGesture = false
            allowFileAccess = true
            allowContentAccess = true
            useWideViewPort = true
            loadWithOverviewMode = true
            setSupportZoom(false)
            displayZoomControls = false
            userAgentString = COBALT_USER_AGENT
            cacheMode = WebSettings.LOAD_DEFAULT
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        }

        setInitialScale(100)
        overScrollMode = View.OVER_SCROLL_NEVER
        isVerticalScrollBarEnabled = false
        isHorizontalScrollBarEnabled = false
        // NOTE: do NOT clearCache() on every launch — it evicts the HTTP/media cache
        // and forces re-download of player JS/CSS plus cold adaptive-streaming
        // startup, worsening 4K buffering on real TV hardware.

        CookieManager.getInstance().apply {
            setAcceptCookie(true)
            setAcceptThirdPartyCookies(this@TVWebView, true)
        }
    }

    private fun setupDocumentStartScript() {
        try {
            if (WebViewFeature.isFeatureSupported(WebViewFeature.DOCUMENT_START_SCRIPT)) {
                val script = context.assets.open("h5vcc_polyfill.js")
                    .bufferedReader()
                    .use { it.readText() }

                WebViewCompat.addDocumentStartJavaScript(this, script, setOf("*"))
                Log.d(TAG, "Successfully bound DOCUMENT_START_SCRIPT for zero-gap ad elimination.")
            }
        } catch (e: Throwable) {
            Log.e(TAG, "Could not bind DOCUMENT_START_SCRIPT, will fallback to WebViewClient: ${e.message}")
        }
    }

    override fun dispatchKeyEvent(event: KeyEvent): Boolean {
        // Forward D-Pad and standard navigation keys directly to the web view DOM
        return super.dispatchKeyEvent(event)
    }

    override fun scrollTo(x: Int, y: Int) {
        // YouTube TV handles all layout and scrolling internally via CSS transforms.
        // Prevent native WebView scrolling which causes vertical viewport displacement.
        super.scrollTo(0, 0)
    }

    override fun computeScroll() {
        super.computeScroll()
        if (scrollX != 0 || scrollY != 0) {
            scrollTo(0, 0)
        }
    }

    override fun overScrollBy(
        deltaX: Int, deltaY: Int,
        scrollX: Int, scrollY: Int,
        scrollRangeX: Int, scrollRangeY: Int,
        maxOverScrollX: Int, maxOverScrollY: Int,
        isTouchEvent: Boolean
    ): Boolean = false
}
