package com.k2.youtubetv.remote

import android.app.Activity
import android.os.SystemClock
import android.util.Log
import android.view.KeyEvent
import android.webkit.WebView
import android.widget.Toast

class TVRemoteKeyHandler(
    private val activity: Activity,
    private val webViewProvider: () -> WebView?
) {

    companion object {
        private const val TAG = "TVRemoteKeyHandler"
        private const val BACK_PRESS_INTERVAL = 2000L
    }

    private var lastBackPressTime: Long = 0L

    fun handleKeyEvent(keyCode: Int, event: KeyEvent): Boolean {
        if (event.action != KeyEvent.ACTION_DOWN) {
            return false
        }

        val webView = webViewProvider() ?: return false

        return when (keyCode) {
            KeyEvent.KEYCODE_BACK, KeyEvent.KEYCODE_ESCAPE -> {
                handleBackAction(webView)
                true
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

                var OVERLAY_SEL = 'dialog, [role="dialog"], [aria-modal="true"], .ytp-popup, .ytp-settings-menu, .ytp-panel, .ytp-contextmenu, .ytp-menu, ytlr-dialog-renderer, ytlr-fullscreen-metadata-renderer, tp-yt-paper-dialog, tp-yt-paper-menu';
                var found = null;
                var foundVia = '';
                var cands = k2DeepQuery(OVERLAY_SEL);
                for (var i = 0; i < cands.length; i++) {
                    if (k2Visible(cands[i])) { found = cands[i]; foundVia = 'sel:' + (cands[i].tagName || '?'); break; }
                }

                // Fallback: visible element with menu/dialog-ish class or id.
                // Always-on chrome (control bars, progress, thumbnails) is excluded.
                if (!found) {
                    var skipTags = {SCRIPT:1, STYLE:1, META:1, LINK:1, HEAD:1, HTML:1, BODY:1, VIDEO:1, SOURCE:1, TRACK:1, CANVAS:1, IMG:1, INPUT:1};
                    var all = document.getElementsByTagName('*');
                    for (var m = 0; m < all.length; m++) {
                        var e = all[m];
                        if (skipTags[e.tagName]) continue;
                        var hay = k2ClassOf(e) + ' ' + (e.id || '');
                        if (!/(menu|dialog|popup|sheet|dropdown|settings|quality|options|overflow|select|listbox)/i.test(hay)) continue;
                        if (/(control-bar|controlbar|player-control|title|progress|seek|spinner|loader|toast|thumbnail|avatar)/i.test(hay)) continue;
                        if (!k2Visible(e)) continue;
                        var looksOpen = (e.getAttribute && (e.getAttribute('aria-expanded') === 'true' || e.getAttribute('aria-modal') === 'true' || (e.hasAttribute && e.hasAttribute('open'))));
                        var hasItems = false;
                        try { hasItems = !!e.querySelector('[role="menuitem"], [role="option"], [role="menuitemradio"], .ytp-menuitem, button'); } catch (e4) {}
                        if (looksOpen || hasItems || /open|show|active|visible|expanded/i.test(hay)) { found = e; foundVia = 'regex'; break; }
                    }
                }

                // Fallback: keyboard focus sitting inside a menu-ish ancestor (climbs out of shadow roots).
                if (!found) {
                    var node = document.activeElement;
                    var guard = 0;
                    while (node && node !== document && node !== document.documentElement && guard < 25) {
                        guard++;
                        var hn = k2ClassOf(node) + ' ' + (node.id || '');
                        var role = (node.getAttribute && node.getAttribute('role')) || '';
                        if (role === 'menuitem' || role === 'option' || role === 'menuitemradio' || role === 'menu' || role === 'listbox' || role === 'dialog') { found = node; foundVia = 'focus-role:' + role; break; }
                        if (node.classList && (node.classList.contains('ytp-menuitem') || node.classList.contains('ytp-panel'))) { found = node; foundVia = 'focus-class'; break; }
                        if (/(menu|dialog|popup|panel|sheet|settings|quality|options|listbox)/i.test(hn) && !/(control-bar|player-control|progress)/i.test(hn)) { found = node; foundVia = 'focus-ancestor'; break; }
                        if (node.parentNode && node.parentNode !== document) node = node.parentNode;
                        else if (node.getRootNode && node.getRootNode() && node.getRootNode().host) node = node.getRootNode().host;
                        else break;
                    }
                }

                if (found) {
                    // Escalating close attempts. NEVER pause/mute/stop the video here.
                    var n = (window._k2MenuBackCount || 0) + 1;
                    window._k2MenuBackCount = n;
                    var target = document.activeElement || found;
                    function fireKey(t, type, key, code, kc) {
                        try {
                            t.dispatchEvent(new KeyboardEvent(type, { key: key, code: code, keyCode: kc, which: kc, bubbles: true, cancelable: true, composed: true }));
                        } catch (e) {}
                    }
                    var closer = null;
                    try {
                        closer = found.querySelector ? found.querySelector('[aria-label*="닫기"], [aria-label*="Close"], [aria-label*="close"], [aria-label*="뒤로"], [aria-label*="Back"], [aria-label*="back"], [class*="close"], [class*="Close"], [class*="back-button"], [class*="BackButton"]') : null;
                    } catch (e) {}
                    if (closer) { try { closer.click(); } catch (e2) {} }
                    fireKey(target, 'keydown', 'Escape', 'Escape', 27);
                    fireKey(target, 'keyup', 'Escape', 'Escape', 27);
                    try { document.documentElement.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true, cancelable: true, composed: true })); } catch (e3) {}
                    fireKey(target, 'keydown', 'Backspace', 'Backspace', 8);
                    fireKey(target, 'keyup', 'Backspace', 'Backspace', 8);
                    fireKey(target, 'keydown', 'BrowserBack', 'BrowserBack', 8);
                    fireKey(target, 'keydown', 'GoBack', 'GoBack', 461);
                    fireKey(target, 'keydown', 'Return', 'Return', 10009);
                    return 'HANDLED_MENU:' + foundVia + '#' + n;
                }
                window._k2MenuBackCount = 0;

                // 2. If NO overlay is open, we are navigating AWAY from video or screen:
                // Stop and mute video to prevent background audio leak
                var isVideoPlaying = false;
                var vids = document.querySelectorAll('video');
                for (var i = 0; i < vids.length; i++) {
                    if (!vids[i].paused || vids[i].currentTime > 0) {
                        isVideoPlaying = true;
                    }
                    try {
                        vids[i].pause();
                        vids[i].muted = true;
                    } catch (e) {}
                }
                var player = document.getElementById('movie_player') || document.querySelector('.html5-video-player');
                if (player) {
                    try { player.stopVideo(); } catch (e) {}
                    try { player.pauseVideo(); } catch (e) {}
                }

                // 3. Leave the watch screen with EXACTLY ONE navigation step.
                // Priority: strict app back button (router-aware) -> remembered
                // browse URL (deterministic return to the list) -> single history
                // step. Stacking actions overshoots to the account picker.
                var backBtn = null;
                try {
                    var _cands = document.querySelectorAll('.yt-tv-navigation-back-button, button[aria-label*="뒤로"], button[aria-label*="Back"], button[aria-label*="back"]');
                    for (var bi = 0; bi < _cands.length; bi++) {
                        if (k2Visible(_cands[bi])) { backBtn = _cands[bi]; break; }
                    }
                } catch (e5) {}
                // Smart fallback: visible back-named button outside account/profile areas.
                if (!backBtn) {
                    try {
                        var _btns = document.getElementsByTagName('button');
                        for (var sj = 0; sj < _btns.length; sj++) {
                            var _b = _btns[sj];
                            var _nm = '';
                            try { _nm = (_b.getAttribute('aria-label') || _b.getAttribute('title') || _b.textContent || ''); } catch (e10) {}
                            if (!/뒤로|back/i.test(_nm)) continue;
                            if (!k2Visible(_b)) continue;
                            var _anc = _b, _inAcct = false, _g = 0;
                            while (_anc && _anc !== document && _g < 8) {
                                _g++;
                                var _hh = k2ClassOf(_anc) + ' ' + (_anc.id || '');
                                if (/account|profile|avatar|signin|login/i.test(_hh)) { _inAcct = true; break; }
                                _anc = _anc.parentElement;
                            }
                            if (!_inAcct) { backBtn = _b; break; }
                        }
                    } catch (e7) {}
                }
                if (backBtn) {
                    var _desc = '';
                    try { _desc = (backBtn.tagName || '?') + '.' + k2ClassOf(backBtn).split(' ').slice(0, 2).join('.') + '("' + (((backBtn.getAttribute && backBtn.getAttribute('aria-label')) || '').substring(0, 24)) + '")'; } catch (e8) {}
                    // Activate via the trusted key path (real DPAD_CENTER dispatched
                    // from the app side): a synthetic .click() may be ignored by the
                    // app, leaving navigation to a history stack that no longer
                    // contains the browse list (overshoot to the account picker).
                    var _fok = false;
                    try { backBtn.focus(); _fok = (document.activeElement === backBtn); } catch (e6) {}
                    if (window._k2NcHref === window.location.href) window._k2NcCount = (window._k2NcCount || 0) + 1;
                    else { window._k2NcHref = window.location.href; window._k2NcCount = 0; }
                    if (_fok && window._k2NcCount < 2) {
                        return 'NEEDS_CENTER:' + _desc;
                    }
                    // Focus failed or center-press proved futile: fall through to
                    // remembered-URL / history navigation below.
                }

                if (window._k2LastBrowse && window._k2LastBrowse !== window.location.href) {
                    try { window.location.replace(window._k2LastBrowse); } catch (e9) {}
                    return 'HANDLED_VIDEO:browse-url';
                }

                if (window.location.href.indexOf('/watch') !== -1 || isVideoPlaying) {
                    window.history.back();
                    return 'HANDLED_VIDEO:history:len=' + window.history.length;
                }

                if (window.history.length > 1) {
                    window.history.back();
                    return 'HANDLED_HISTORY:len=' + window.history.length;
                }

                return 'ROOT:len=' + window.history.length;
            })();
        """.trimIndent()

        webView.evaluateJavascript(script) { result ->
            val cleanedResult = result?.replace("\"", "") ?: ""
            Log.d(TAG, "Back navigation result: $cleanedResult")
            if (cleanedResult.startsWith("NEEDS_CENTER")) {
                // Trusted activation: real DPAD_CENTER key down+up into the WebView
                // so the app's own key system presses the focused back button.
                webView.dispatchKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_DPAD_CENTER))
                webView.dispatchKeyEvent(KeyEvent(KeyEvent.ACTION_UP, KeyEvent.KEYCODE_DPAD_CENTER))
                lastBackPressTime = 0L
            } else if (cleanedResult.startsWith("HANDLED_MENU") || cleanedResult.startsWith("HANDLED_VIDEO") || cleanedResult.startsWith("HANDLED_HISTORY")) {
                // Successfully handled navigation or closed menu, reset timer
                lastBackPressTime = 0L
            } else if (webView.canGoBack()) {
                webView.goBack()
                lastBackPressTime = 0L
            } else {
                // At the root home screen, double back to exit app
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
