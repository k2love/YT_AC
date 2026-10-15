package com.k2.youtubetv

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.KeyEvent
import android.view.View
import android.view.WindowManager
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.k2.youtubetv.auth.GoogleAuthManager
import com.k2.youtubetv.bridge.CobaltJsBridge
import com.k2.youtubetv.bridge.PlatformServiceRouter
import com.k2.youtubetv.databinding.ActivityMainBinding
import com.k2.youtubetv.remote.TVRemoteKeyHandler
import com.k2.youtubetv.update.AppUpdateManager
import com.k2.youtubetv.webview.TVWebChromeClient
import com.k2.youtubetv.webview.TVWebViewClient
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "MainActivity"
        private const val BASE_URL = "https://www.youtube.com/tv"
    }

    private lateinit var binding: ActivityMainBinding
    private lateinit var router: PlatformServiceRouter
    private lateinit var jsBridge: CobaltJsBridge
    private lateinit var remoteKeyHandler: TVRemoteKeyHandler
    private lateinit var webChromeClient: TVWebChromeClient
    private lateinit var googleAuthManager: GoogleAuthManager
    private lateinit var appUpdateManager: AppUpdateManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        hideSystemUI()

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        router = PlatformServiceRouter(applicationContext) { binding.webView }
        jsBridge = CobaltJsBridge(router)
        appUpdateManager = AppUpdateManager(this)
        remoteKeyHandler = TVRemoteKeyHandler(this, { binding.webView }) {
            appUpdateManager.showSettingsDialog()
        }
        googleAuthManager = GoogleAuthManager(applicationContext, router.syncAuthService)

        setupWebView()
        loadTargetUrl(intent)

        lifecycleScope.launch {
            googleAuthManager.syncDeviceGoogleAccountIfAvailable()
            appUpdateManager.checkForUpdates(isManualCheck = false)
        }
    }

    private fun setupWebView() {
        webChromeClient = TVWebChromeClient(binding.customViewContainer, binding.webView)
        binding.webView.apply {
            webViewClient = TVWebViewClient(applicationContext)
            this@apply.webChromeClient = this@MainActivity.webChromeClient
            addJavascriptInterface(jsBridge, CobaltJsBridge.INTERFACE_NAME)
            addJavascriptInterface(object {
                @android.webkit.JavascriptInterface
                fun checkAppUpdate() {
                    runOnUiThread {
                        appUpdateManager.showSettingsDialog()
                    }
                }
            }, "YT_TV_APP")
        }
    }

    private fun loadTargetUrl(intent: Intent?) {
        val isRemoteButton = intent?.getBooleanExtra("remote_button", false) == true
        val launchParam = if (isRemoteButton) "launch=remote" else "launch=menu"
        val targetUrl = "$BASE_URL?$launchParam"

        Log.d(TAG, "Loading YouTube TV URL: $targetUrl")
        binding.webView.loadUrl(targetUrl)
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        setIntent(intent)
        loadTargetUrl(intent)
    }

    override fun dispatchKeyEvent(event: KeyEvent): Boolean {
        if (webChromeClient.isCustomViewShowing() && event.keyCode == KeyEvent.KEYCODE_BACK && event.action == KeyEvent.ACTION_DOWN) {
            webChromeClient.onHideCustomView()
            return true
        }

        if (remoteKeyHandler.handleKeyEvent(event.keyCode, event)) {
            return true
        }

        return super.dispatchKeyEvent(event)
    }

    private fun hideSystemUI() {
        window.decorView.systemUiVisibility = (
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                or View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                or View.SYSTEM_UI_FLAG_FULLSCREEN
        )
    }

    override fun onResume() {
        super.onResume()
        hideSystemUI()
        binding.webView.onResume()
        router.syncAuthService.reportSavedCredentialIfValid()
    }

    override fun onPause() {
        super.onPause()
        binding.webView.onPause()
    }

    override fun onDestroy() {
        super.onDestroy()
        binding.webView.destroy()
    }
}
