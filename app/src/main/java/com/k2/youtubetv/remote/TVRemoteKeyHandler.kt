package com.k2.youtubetv.remote

import android.app.Activity
import android.os.SystemClock
import android.util.Log
import android.view.KeyEvent
import android.webkit.WebView
import android.widget.Toast

class TVRemoteKeyHandler(
    private val activity: Activity,
    private val webViewProvider: () -> WebView?,
    private val onOpenSettings: (() -> Unit)? = null
) {

    companion object {
        private const val TAG = "TVRemoteKeyHandler"
        private const val BACK_PRESS_INTERVAL = 2000L
    }

    private var lastBackPressTime: Long = 0L

    fun handleKeyEvent(keyCode: Int, event: KeyEvent): Boolean {
        if (event.action == KeyEvent.ACTION_UP && (keyCode == KeyEvent.KEYCODE_BACK || keyCode == KeyEvent.KEYCODE_ESCAPE)) {
            // Consume ACTION_UP as well to prevent default Activity/WebView back propagation
            return true
        }

        if (event.action != KeyEvent.ACTION_DOWN) {
            return false
        }

        val webView = webViewProvider() ?: return false

        return when (keyCode) {
            KeyEvent.KEYCODE_BACK, KeyEvent.KEYCODE_ESCAPE -> {
                handleBackAction(webView)
                true
            }
            KeyEvent.KEYCODE_MENU, KeyEvent.KEYCODE_SETTINGS -> {
                if (onOpenSettings != null) {
                    onOpenSettings.invoke()
                    true
                } else false
            }
            KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE -> {
                dispatchJsKeyEvent(webView, "k", 75) // YouTube toggle play/pause shortcut
                true
            }
            KeyEvent.KEYCODE_MEDIA_PLAY -> {
                evaluateJs(webView, "var v = document.querySelector('video'); if (v && v.paused) v.play();")
                true
            }
            KeyEvent.KEYCODE_MEDIA_PAUSE -> {
                evaluateJs(webView, "var v = document.querySelector('video'); if (v && !v.paused) v.pause();")
                true
            }
            KeyEvent.KEYCODE_MEDIA_FAST_FORWARD -> {
                dispatchJsKeyEvent(webView, "l", 76) // YouTube 10s forward shortcut
                true
            }
            KeyEvent.KEYCODE_MEDIA_REWIND -> {
                dispatchJsKeyEvent(webView, "j", 74) // YouTube 10s backward shortcut
                true
            }
            KeyEvent.KEYCODE_SEARCH -> {
                dispatchJsKeyEvent(webView, "/", 191)
                true
            }
            KeyEvent.KEYCODE_INFO -> {
                dispatchJsKeyEvent(webView, "i", 73)
                true
            }
            else -> false
        }
    }

    private fun handleBackAction(webView: WebView) {
        // NOTE: the overlay menu is closed WITHOUT touching the video. The
        // video is paused/stopped ONLY when no overlay is open (real navigate-away).
        // Detection pierces shadow DOM and falls back to menu-ish class/id patterns,
        // because YouTube renames its obfuscated TV-framework classes frequently.
        val script = """
            (function() {
                function k2ClassOf(el) {
                    try {
                        var c = el.className;
                        if (c == null) return '';
                        if (typeof c === 'string') return c;
                        if (c.baseVal !== undefined) return String(c.baseVal);
                        return String(c);
                    } catch (e) { return ''; }
                }

                function k2DeepQuery(selector) {
                    var out = [];
                    function walk(root) {
                        var list = null;
                        try { list = root.querySelectorAll(selector); } catch (e) { return; }
                        for (var i = 0; i < list.length; i++) out.push(list[i]);
                        var all = null;
                        try { all = root.querySelectorAll('*'); } catch (e2) { return; }
                        for (var j = 0; j < all.length; j++) {
                            try { if (all[j].shadowRoot) walk(all[j].shadowRoot); } catch (e3) {}
                        }
                    }
                    walk(document);
                    return out;
                }

                function k2Visible(el) {
                    if (!el || !el.getBoundingClientRect) return false;
                    if (el === document.body || el === document.documentElement || el.tagName === 'BODY' || el.tagName === 'HTML') return false;
                    try {
                        if (el.tagName === 'DIALOG' && el.hasAttribute && !el.hasAttribute('open')) return false;
                        var cs = window.getComputedStyle(el);
                        if (!cs || cs.display === 'none' || cs.visibility === 'hidden' || cs.visibility === 'collapse') return false;
                        if (cs.opacity === '0') return false;
                        var r = el.getBoundingClientRect();
                        if (r.width <= 0 || r.height <= 0) return false;
                        if (el.offsetParent === null && cs.position !== 'fixed' && cs.position !== 'sticky') return false;
                        return true;
                    } catch (e) { return false; }
                }

                function fireKey(t, type, key, code, kc) {
                    try {
                        t.dispatchEvent(new KeyboardEvent(type, { key: key, code: code, keyCode: kc, which: kc, bubbles: true, cancelable: true, composed: true }));
                    } catch (e) {}
                }

                var OVERLAY_SEL = 'dialog, [role="dialog"], [aria-modal="true"], .ytp-popup, .ytp-settings-menu, .ytp-panel, .ytp-contextmenu, .ytp-menu, ytlr-dialog-renderer, ytlr-fullscreen-metadata-renderer, tp-yt-paper-dialog, tp-yt-paper-menu';
                var found = null;
                var foundVia = '';
                var cands = k2DeepQuery(OVERLAY_SEL);
                for (var i = 0; i < cands.length; i++) {
                    if (k2Visible(cands[i])) { found = cands[i]; foundVia = 'sel:' + (cands[i].tagName || '?'); break; }
                }

                // Fallback: visible element with menu/dialog-ish class or id.
                // Always-on chrome (control bars, progress, thumbnails, app-quality-root) is excluded.
                if (!found) {
                    var skipTags = {SCRIPT:1, STYLE:1, META:1, LINK:1, HEAD:1, HTML:1, BODY:1, VIDEO:1, SOURCE:1, TRACK:1, CANVAS:1, IMG:1, INPUT:1};
                    var all = document.getElementsByTagName('*');
                    for (var m = 0; m < all.length; m++) {
                        var e = all[m];
                        if (skipTags[e.tagName]) continue;
                        var hay = k2ClassOf(e) + ' ' + (e.id || '');
                        if (!/(menu|dialog|popup|sheet|dropdown|settings|quality|options|overflow|select|listbox)/i.test(hay)) continue;
                        if (/(control-bar|controlbar|player-control|title|progress|seek|spinner|loader|toast|thumbnail|avatar|app-quality-root)/i.test(hay)) continue;
                        if (!k2Visible(e)) continue;
                        var looksOpen = (e.getAttribute && (e.getAttribute('aria-expanded') === 'true' || e.getAttribute('aria-modal') === 'true' || (e.hasAttribute && e.hasAttribute('open'))));
                        var hasItems = false;
                        try { hasItems = !!e.querySelector('[role="menuitem"], [role="option"], [role="menuitemradio"], .ytp-menuitem, button'); } catch (e4) {}
                        if (looksOpen || hasItems || /open|show|active|visible|expanded/i.test(hay)) { found = e; foundVia = 'regex:' + e.tagName; break; }
                    }
                }

                // Fallback: keyboard focus sitting inside a menu-ish ancestor (never climb into BODY/HTML).
                if (!found) {
                    var node = document.activeElement;
                    var guard = 0;
                    while (node && node !== document && node !== document.documentElement && node !== document.body && guard < 25) {
                        guard++;
                        if (node.tagName === 'BODY' || node.tagName === 'HTML') break;
                        var hn = k2ClassOf(node) + ' ' + (node.id || '');
                        var role = (node.getAttribute && node.getAttribute('role')) || '';
                        if (role === 'menuitem' || role === 'option' || role === 'menuitemradio' || role === 'menu' || role === 'listbox' || role === 'dialog') { found = node; foundVia = 'focus-role:' + role; break; }
                        if (node.classList && (node.classList.contains('ytp-menuitem') || node.classList.contains('ytp-panel'))) { found = node; foundVia = 'focus-class'; break; }
                        if (/(menu|dialog|popup|panel|sheet|settings|quality|options|listbox)/i.test(hn) && !/(control-bar|player-control|progress|app-quality-root)/i.test(hn)) { found = node; foundVia = 'focus-ancestor'; break; }
                        if (node.parentNode && node.parentNode !== document) node = node.parentNode;
                        else if (node.getRootNode && node.getRootNode() && node.getRootNode().host) node = node.getRootNode().host;
                        else break;
                    }
                }

                if (found && found !== document.body && found.tagName !== 'BODY') {
                    // Close the overlay menu without touching video playback
                    var closer = null;
                    try {
                        var buttons = found.querySelectorAll('button, [role="button"], [class*="close"], [class*="back"], [aria-label]');
                        for (var b = 0; b < buttons.length; b++) {
                            var btn = buttons[b];
                            var lbl = (btn.getAttribute('aria-label') || '').trim();
                            var cls = k2ClassOf(btn);
                            if (/(건너뜁니다|초\s*뒤|seek|scrub|시작하려면)/i.test(lbl)) continue;
                            if (/^(닫기|취소|뒤로|close|back|cancel)$/i.test(lbl) ||
                                /^(close|back|cancel)-?button/i.test(cls) ||
                                /(ytp-panel-back-button|ytp-settings-button|ytp-close-button)/i.test(cls)) {
                                closer = btn;
                                break;
                            }
                        }
                    } catch (e) {}
                    if (closer) {
                        try { closer.click(); return 'HANDLED_MENU:closer_clicked'; } catch (e2) {}
                    }
                    return 'NEEDS_ESCAPE:menu';
                }

                // 2. Check if a video is active or in Watch screen
                var isVideoActive = false;
                var vids = document.querySelectorAll('video');
                for (var i = 0; i < vids.length; i++) {
                    if (!vids[i].paused || vids[i].currentTime > 0 || vids[i].readyState >= 1) {
                        isVideoActive = true;
                    }
                }
                var player = document.getElementById('movie_player') || document.querySelector('.html5-video-player');
                if (player) {
                    if (typeof player.getPlayerState === 'function') {
                        var s = player.getPlayerState();
                        if (s === 1 || s === 2 || s === 3) isVideoActive = true;
                    }
                    if (player.classList && player.classList.contains('playing-mode')) isVideoActive = true;
                }
                var curHref = window.location.href;
                var curHash = window.location.hash || '';
                if (curHref.indexOf('/watch') !== -1 || curHash.indexOf('watch') !== -1) {
                    isVideoActive = true;
                }
                if (document.querySelector('ytlr-watch-metadata-renderer, ytlr-player-controls')) {
                    isVideoActive = true;
                }

                if (isVideoActive) {
                    // Check if player controls/HUD or watch metadata is visibly open
                    var controlsActive = false;
                    var playerControls = document.querySelector('.ytp-chrome-bottom, ytlr-player-controls, ytlr-watch-metadata-renderer');
                    if (playerControls && k2Visible(playerControls)) {
                        controlsActive = true;
                    }

                    if (controlsActive) {
                        // User has HUD open while watching video -> Escape closes the HUD without stopping playback
                        return 'NEEDS_ESCAPE:hud';
                    }

                    // Fullscreen video playback with no HUD -> User wants to EXIT video back to browse/home
                    for (var j = 0; j < vids.length; j++) {
                        try {
                            vids[j].pause();
                            vids[j].muted = true;
                        } catch (e5) {}
                    }
                    if (player) {
                        try { player.stopVideo(); } catch (e6) {}
                        try { player.pauseVideo(); } catch (e7) {}
                        try { player.focus(); } catch (e8) {}
                    }

                    // Arm back-navigation flag to block any account selector redirect
                    window._k2InBackNavigation = true;
                    setTimeout(function() { window._k2InBackNavigation = false; }, 1500);

                    return 'NEEDS_ESCAPE:video';
                }

                // 3. Sub-page navigation (Settings, Search, Channel, Library, Playlist, etc.)
                var isRootHome = (curHash === '' || curHash === '#/' || curHash === '#/home' || curHash === '#/browse');
                if (!isRootHome) {
                    return 'NEEDS_ESCAPE:subpage';
                }

                // 4. Truly at root home: NEVER fire Escape or Back into WebView!
                // Firing Escape at root home causes Kabuki to pop the stack and crash into the Account Selector!
                return 'ROOT_HOME';
            })();
        """.trimIndent()

        webView.evaluateJavascript(script) { result ->
            val cleanedResult = result?.replace("\"", "") ?: ""
            Log.d(TAG, "Back navigation result: $cleanedResult")
            if (cleanedResult.startsWith("NEEDS_ESCAPE") || cleanedResult.startsWith("HANDLED_MENU")) {
                if (cleanedResult.startsWith("NEEDS_ESCAPE")) {
                    // Dispatch real trusted Escape key to WebView so Blink processes it natively
                    webView.dispatchKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_ESCAPE))
                    webView.dispatchKeyEvent(KeyEvent(KeyEvent.ACTION_UP, KeyEvent.KEYCODE_ESCAPE))
                }
                lastBackPressTime = 0L
            } else {
                // At the root home screen: double back to exit app.
                // NO keys are forwarded to WebView so it stays stably on Home!
                val now = SystemClock.elapsedRealtime()
                if (now - lastBackPressTime < BACK_PRESS_INTERVAL) {
                    activity.finish()
                } else {
                    lastBackPressTime = now
                    Toast.makeText(activity, "뒤로 가기 버튼을 한 번 더 누르면 종료됩니다.", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    fun handleBackFromActivity() {
        val webView = webViewProvider() ?: return
        handleBackAction(webView)
    }

    private fun dispatchJsKeyEvent(webView: WebView, key: String, keyCode: Int) {
        val script = """
            (function() {
                var event = new KeyboardEvent('keydown', {
                    key: '$key',
                    code: '$key',
                    keyCode: $keyCode,
                    which: $keyCode,
                    bubbles: true,
                    cancelable: true
                });
                var target = document.activeElement || document.body;
                target.dispatchEvent(event);
            })();
        """.trimIndent()
        webView.evaluateJavascript(script, null)
    }

    private fun evaluateJs(webView: WebView, js: String) {
        webView.evaluateJavascript(js, null)
    }
}
