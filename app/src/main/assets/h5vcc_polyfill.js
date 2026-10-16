(function() {
    if (window._h5vcc_adblock_v8_initialized) {
        return;
    }
    window._h5vcc_adblock_v8_initialized = true;

    console.log("[ZeroAd] Initializing Ultra-Clean Zero-Ad v8 (4K UHD Safe Unlock + Pure Transparent Overlays)...");

    // =========================================================================
    // 0. 4K (2160p) Display Resolution & Ultra HD Codec Safe Unlocking
    // =========================================================================
    try {
        // Report 4K UHD display resolution to unlock 2160p adaptive formats
        Object.defineProperty(window.screen, 'width', { get: function() { return 3840; }, configurable: true });
        Object.defineProperty(window.screen, 'height', { get: function() { return 2160; }, configurable: true });
        Object.defineProperty(window.screen, 'availWidth', { get: function() { return 3840; }, configurable: true });
        Object.defineProperty(window.screen, 'availHeight', { get: function() { return 2160; }, configurable: true });
        Object.defineProperty(window, 'devicePixelRatio', { get: function() { return 2.0; }, configurable: true });

        // Safely unlock VP9, AV1, 4K/8K & HFR (60fps) formats in MediaSource without breaking EME/DRM
        if (window.MediaSource && typeof window.MediaSource.isTypeSupported === 'function') {
            var origIsTypeSupported = window.MediaSource.isTypeSupported.bind(window.MediaSource);
            window.MediaSource.isTypeSupported = function(mimeType) {
                if (!mimeType) return false;
                var lower = mimeType.toLowerCase();

                // YouTube TV sanity probe defense:
                // Reject impossible probe values (Ip) explicitly so the player's
                // cross-check (valid && !invalid) passes. Without this, Chromium MSE
                // returns true for impossible probes (e.g. framerate=9999, height=99999),
                // causing the player to flag the device as lying and cap HFR (>32fps) to 480p/720p!
                var fpsM = lower.match(/framerate\s*=\s*(\d+)/);
                if (fpsM && parseInt(fpsM[1], 10) > 120) return false;

                var hM = lower.match(/height\s*=\s*(\d+)/);
                if (hM && parseInt(hM[1], 10) > 4320) return false;

                var wM = lower.match(/width\s*=\s*(\d+)/);
                if (wM && parseInt(wM[1], 10) > 7680) return false;

                var brM = lower.match(/bitrate\s*=\s*(\d+)/);
                if (brM && parseInt(brM[1], 10) >= 20000000) return false;

                var chM = lower.match(/channels\s*=\s*(\d+)/);
                if (chM && parseInt(chM[1], 10) > 8) return false;

                if (lower.indexOf('catavision') !== -1 ||
                    lower.indexOf('invalidformat') !== -1 ||
                    lower.indexOf('decode-to-texture=nope') !== -1 ||
                    lower.indexOf('av99') !== -1 ||
                    lower.indexOf('experimental=invalid') !== -1 ||
                    lower.indexOf('tunnelmode=false') !== -1) {
                    return false;
                }

                // For normal realistic parameters (framerate<=120, height<=4320, etc.)
                // or bare queries, affirm proven codecs so HFR/4K/8K formats are unlocked.
                if (lower.indexOf('vp09') !== -1 ||
                    lower.indexOf('vp9') !== -1 ||
                    lower.indexOf('vp08') !== -1 ||
                    lower.indexOf('vp8') !== -1 ||
                    lower.indexOf('av01') !== -1 ||
                    lower.indexOf('avc1') !== -1 ||
                    lower.indexOf('mp4a') !== -1 ||
                    lower.indexOf('opus') !== -1 ||
                    lower.indexOf('vorbis') !== -1 ||
                    lower.indexOf('ec-3') !== -1 ||
                    lower.indexOf('ec3') !== -1 ||
                    lower.indexOf('ac-3') !== -1 ||
                    lower.indexOf('ac3') !== -1) {
                    return true;
                }
                return origIsTypeSupported(mimeType);
            };
        }
        // NOTE: window.innerWidth/innerHeight must NEVER be spoofed. They define the
        // CSS layout viewport: combined with loadWithOverviewMode, a lied width
        // makes WebView zoom out to fit it (e.g. 1920 forced into a real 1280 ->
        // 0.667 zoom -> UI squeezed into the top 2/3, bottom 1/3 black).
        // Viewport-based quality caps are handled by the native tv-player-ias.js
        // patch (B3/k2) instead, which does not affect layout.

        // Force MediaCapabilities decoding probes to report full support.
        // The player gates 4K/8K ladders on decodingInfo(); a "supported:false"
        // answer for VP9/AV1 2160p locks the quality menu to 720p regardless of
        // JS patches, so answer affirmatively without breaking EME/DRM.
        try {
            var _affirmDecoding = function() {
                return Promise.resolve({ supported: true, smooth: true, powerEfficient: true });
            };
            if (navigator.mediaCapabilities) {
                try { navigator.mediaCapabilities.decodingInfo = _affirmDecoding; } catch (e3) {}
            }
            if (typeof MediaCapabilities !== 'undefined' && MediaCapabilities.prototype) {
                try { MediaCapabilities.prototype.decodingInfo = _affirmDecoding; } catch (e4) {}
            }
        } catch (e5) {
            console.warn("[ZeroAd] mediaCapabilities unlock warning:", e5);
        }

        // Report VP9/AV1/HEVC as playable so format-support checks never filter
        // out UHD adaptive streams.
        try {
            if (window.HTMLMediaElement && HTMLMediaElement.prototype && typeof HTMLMediaElement.prototype.canPlayType === 'function') {
                var _origCPT = HTMLMediaElement.prototype.canPlayType;
                HTMLMediaElement.prototype.canPlayType = function(mime) {
                    if (mime && /vp0?9|vp0?8|av0?1|avc1|mp4a|opus|ec-?3/i.test(mime)) return 'probably';
                    try { return _origCPT.call(this, mime); } catch (e6) { return ''; }
                };
            }
        } catch (e7) {
            console.warn("[ZeroAd] canPlayType unlock warning:", e7);
        }
    } catch (e) {
        console.warn("[ZeroAd] 4K safe unlock warning:", e);
    }

    // =========================================================================
    // 1. Recursive JSON Sanitizer for ALL InnerTube / Player / AdBreak Responses
    // =========================================================================
    var AD_KEYS = {
        'adslotrenderer': true,
        'infeedadrenderer': true,
        'mastheadadrenderer': true,
        'mastheadrenderer': true,
        'heroadrenderer': true,
        'promotedvideorenderer': true,
        'promotedsparkleswebrenderer': true,
        'statementbannerrenderer': true,
        'bannerpromorenderer': true,
        'brandvideorenderer': true,
        'adbreakservicerenderer': true,
        'playerads': true,
        'adbreakheartbeatparams': true,
        'interstitials': true,
        'adbreakrenderer': true,
        'instreamadbreakrenderers': true,
        'adunit': true,
        'adlayouts': true
    };

    function k2ExpandSpeedItemsInArray(items) {
        if (!Array.isArray(items) || items.length === 0) return;
        var hasSpeedItem = false;
        var template2xItem = null;
        for (var si = 0; si < items.length; si++) {
            var it = items[si];
            var clr = it && it.compactLinkRenderer;
            if (clr && clr.serviceEndpoint && clr.serviceEndpoint.commandExecutorCommand) {
                var cmds = clr.serviceEndpoint.commandExecutorCommand.commands || [];
                for (var ci = 0; ci < cmds.length; ci++) {
                    var scs = cmds[ci].setClientSettingEndpoint;
                    if (scs && scs.settingDatas) {
                        for (var sdi = 0; sdi < scs.settingDatas.length; sdi++) {
                            if (scs.settingDatas[sdi].clientSettingEnum &&
                                scs.settingDatas[sdi].clientSettingEnum.item === "PLAYBACK_SPEED") {
                                hasSpeedItem = true;
                                var iv = String(scs.settingDatas[sdi].intValue);
                                if (iv === "2" || iv === "2.0") {
                                    template2xItem = it;
                                }
                            }
                        }
                    }
                }
            }
        }
        if (hasSpeedItem && template2xItem) {
            var alreadyHas4x = items.some(function(item) {
                var t = item && item.compactLinkRenderer && item.compactLinkRenderer.title && item.compactLinkRenderer.title.simpleText;
                return t && (t.indexOf('4\u00d7') !== -1 || t.indexOf('4x') !== -1);
            });
            if (!alreadyHas4x) {
                var extraSpeeds = [
                    { label: '2.25\u00d7', val: '2.25' },
                    { label: '2.5\u00d7', val: '2.5' },
                    { label: '2.75\u00d7', val: '2.75' },
                    { label: '3\u00d7', val: '3' },
                    { label: '3.5\u00d7', val: '3.5' },
                    { label: '4\u00d7', val: '4' }
                ];
                for (var ei = 0; ei < extraSpeeds.length; ei++) {
                    try {
                        var extraItem = JSON.parse(JSON.stringify(template2xItem));
                        extraItem.compactLinkRenderer.title.simpleText = extraSpeeds[ei].label;
                        if (extraItem.compactLinkRenderer.secondaryIcon) {
                            extraItem.compactLinkRenderer.secondaryIcon.iconType = 'RADIO_BUTTON_UNCHECKED';
                        }
                        var eCmds = extraItem.compactLinkRenderer.serviceEndpoint.commandExecutorCommand.commands;
                        for (var ec = 0; ec < eCmds.length; ec++) {
                            if (eCmds[ec].setClientSettingEndpoint && eCmds[ec].setClientSettingEndpoint.settingDatas) {
                                eCmds[ec].setClientSettingEndpoint.settingDatas[0].intValue = extraSpeeds[ei].val;
                            }
                        }
                        items.push(extraItem);
                    } catch (eExp) {}
                }
            }
        }
    }

    function sanitizeAdsDirectly(obj) {
        if (!obj || typeof obj !== 'object') return;

        // Player & AdBreak properties annihilation
        if ('adPlacements' in obj) {
            obj.adPlacements = [];
        }
        if ('adSlots' in obj) {
            obj.adSlots = [];
        }
        if ('playerAds' in obj) {
            delete obj.playerAds;
        }
        if ('adBreakHeartbeatParams' in obj) {
            delete obj.adBreakHeartbeatParams;
        }
        if ('getAdBreakUrl' in obj) {
            delete obj.getAdBreakUrl;
        }
        if ('playbackTracking' in obj && obj.playbackTracking) {
            delete obj.playbackTracking.ptrackingUrl;
            delete obj.playbackTracking.qoeUrl;
            delete obj.playbackTracking.atrUrl;
        }

        if (Array.isArray(obj)) {
            k2ExpandSpeedItemsInArray(obj);
            for (var i = obj.length - 1; i >= 0; i--) {
                var item = obj[i];
                if (typeof item === 'string') {
                    // Help/feedback URLs inside arrays (e.g. renderer texts[])
                    // never reach the object branch: rewrite them here.
                    if (item.indexOf('youtube.com/tv_help') !== -1) {
                        obj[i] = item.split('youtube.com/tv_help').join(K2_GITHUB_URL_TEXT);
                    } else if (item.indexOf('youtube.com/tv/feedback') !== -1) {
                        obj[i] = item.split('youtube.com/tv/feedback').join(K2_GITHUB_PULLS_URL_TEXT);
                    }
                    continue;
                }
                if (item && typeof item === 'object') {
                    var isAd = false;
                    for (var k in item) {
                        if (AD_KEYS[k.toLowerCase()]) {
                            isAd = true;
                            break;
                        }
                    }
                    if (isAd) {
                        obj.splice(i, 1);
                        continue;
                    }

                    // Purge YouTube Premium upsell tab & action renderer from settings payload
                    if (item.tabRenderer) {
                        var tr = item.tabRenderer;
                        var tabTitle = '';
                        if (tr.title) {
                            if (typeof tr.title === 'string') tabTitle = tr.title;
                            else if (tr.title.simpleText) tabTitle = tr.title.simpleText;
                            else if (Array.isArray(tr.title.runs)) tabTitle = tr.title.runs.map(function(r){return r.text;}).join('');
                        }
                        if (/Premium|프리미엄/i.test(tabTitle)) {
                            obj.splice(i, 1);
                            continue;
                        }
                    }
                    if (item.settingActionRenderer) {
                        var sar = item.settingActionRenderer;
                        var sarTitle = '';
                        if (sar.title) {
                            if (typeof sar.title === 'string') sarTitle = sar.title;
                            else if (sar.title.simpleText) sarTitle = sar.title.simpleText;
                            else if (Array.isArray(sar.title.runs)) sarTitle = sar.title.runs.map(function(r){return r.text;}).join('');
                        }
                        if (/Premium|프리미엄/i.test(sarTitle)) {
                            obj.splice(i, 1);
                            continue;
                        }
                    }
                }
                sanitizeAdsDirectly(item);
            }
        } else {
            if (obj.items && Array.isArray(obj.items)) {
                k2ExpandSpeedItemsInArray(obj.items);
            }
            if (obj.granularVariableSpeedConfig && typeof obj.granularVariableSpeedConfig === 'object') {
                obj.granularVariableSpeedConfig.maximumPlaybackRate = 400;
            }
            for (var key in obj) {
                var lower = key.toLowerCase();
                if (AD_KEYS[lower]) {
                    delete obj[key];
                } else if ((lower.indexOf('quality_cap') !== -1 ||
                            lower.indexOf('max_vertical_resolution') !== -1 ||
                            lower.indexOf('chipset_soft_cap') !== -1) &&
                           typeof obj[key] === 'number') {
                    // Server-driven quality cap flag -> raise to 8K 4320p.
                    obj[key] = 4320;
                } else if (typeof obj[key] === 'string' && obj[key].indexOf('youtube.com/tv_help') !== -1) {
                    // Help Center URL -> GitHub repo (rewritten pre-render: zero flash).
                    obj[key] = obj[key].split('youtube.com/tv_help').join(K2_GITHUB_URL_TEXT);
                } else if (typeof obj[key] === 'string' && obj[key].indexOf('youtube.com/tv/feedback') !== -1) {
                    // Feedback URL -> GitHub pulls (rewritten pre-render: zero flash).
                    obj[key] = obj[key].split('youtube.com/tv/feedback').join(K2_GITHUB_PULLS_URL_TEXT);
                } else if (typeof obj[key] === 'string' && obj[key].length > 2000 &&
                           obj[key].indexOf('data:image') !== -1 && obj[key].indexOf(';base64,') !== -1) {
                    // QR artwork sibling to a help/feedback URL marker -> swap the
                    // image bytes only (wrappers like url("...") preserved). Length
                    // guard keeps small icons untouched; already-swapped values
                    // no longer carry the original markers, so this is one-shot.
                    var _markHelp = false, _markFb = false;
                    for (var _sk in obj) {
                        if (_sk === key) continue;
                        var _sv = null;
                        try { _sv = obj[_sk]; } catch (_e0) {}
                        if (typeof _sv === 'string') {
                            if (_sv.indexOf('youtube.com/tv_help') !== -1) { _markHelp = true; break; }
                            if (_sv.indexOf('youtube.com/tv/feedback') !== -1) { _markFb = true; break; }
                        } else if (_sv && typeof _sv === 'object') {
                            try {
                                var _sj = JSON.stringify(_sv);
                                if (_sj.indexOf('youtube.com/tv_help') !== -1) { _markHelp = true; break; }
                                if (_sj.indexOf('youtube.com/tv/feedback') !== -1) { _markFb = true; break; }
                            } catch (_e1) {}
                        }
                    }
                    var _qrFull = _markHelp ? K2_GITHUB_QR_DATA_URL : (_markFb ? K2_GITHUB_PULLS_QR_DATA_URL : null);
                    if (_qrFull) {
                        obj[key] = obj[key].replace(/data:image\/[a-zA-Z0-9+.-]+;base64,[A-Za-z0-9+/=]+/, _qrFull);
                    }
                } else {
                    sanitizeAdsDirectly(obj[key]);
                }
            }
        }
    }

    // =========================================================================
    // 2. Global JSON.parse Interceptor (Catches 100% of player and ad break payloads)
    // =========================================================================
    try {
        var originalJsonParse = JSON.parse;
        JSON.parse = function() {
            var result = originalJsonParse.apply(this, arguments);
            if (result && typeof result === 'object') {
                sanitizeAdsDirectly(result);
            }
            return result;
        };
    } catch (e) {
        console.warn("[ZeroAd] JSON.parse hook warning:", e);
    }

    // =========================================================================
    // 3. Hook window.fetch & XMLHttpRequest
    // =========================================================================
    var originalFetch = window.fetch;
    window.fetch = async function() {
        var args = Array.prototype.slice.call(arguments);
        var url = typeof args[0] === 'string' ? args[0] : (args[0] && args[0].url ? args[0].url : '');

        // Immediately drop all ad beacons, midrolls, and ad break triggers
        if (url.indexOf('/api/stats/ads') !== -1 ||
            url.indexOf('/pagead/') !== -1 ||
            url.indexOf('doubleclick.net') !== -1 ||
            url.indexOf('/youtubei/v1/att/') !== -1 ||
            url.indexOf('/ptracking') !== -1 ||
            url.indexOf('/get_midroll_info') !== -1 ||
            url.indexOf('/player/ad_break') !== -1) {
            return new Response('{}', { status: 200, headers: { 'Content-Type': 'application/json' } });
        }

        var response = await originalFetch.apply(this, args);

        if (url.indexOf('/youtubei/v1/') !== -1) {
            try {
                var clone = response.clone();
                var text = await clone.text();
                var json = JSON.parse(text); // Automatically sanitized by JSON.parse hook

                return new Response(JSON.stringify(json), {
                    status: response.status,
                    statusText: response.statusText,
                    headers: response.headers
                });
            } catch (e) {
                return response;
            }
        }

        return response;
    };

    var originalOpen = XMLHttpRequest.prototype.open;
    var originalSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url) {
        this._reqUrl = url;
        return originalOpen.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function() {
        var self = this;
        if (self._reqUrl && (
            self._reqUrl.indexOf('/api/stats/ads') !== -1 ||
            self._reqUrl.indexOf('/pagead/') !== -1 ||
            self._reqUrl.indexOf('doubleclick.net') !== -1 ||
            self._reqUrl.indexOf('/ptracking') !== -1 ||
            self._reqUrl.indexOf('/get_midroll_info') !== -1 ||
            self._reqUrl.indexOf('/player/ad_break') !== -1
        )) {
            return;
        }

        if (self._reqUrl && self._reqUrl.indexOf('/youtubei/v1/') !== -1) {
            self.addEventListener('readystatechange', function() {
                if (self.readyState === 4 && self.status === 200) {
                    try {
                        var json = JSON.parse(self.responseText);
                        var modified = JSON.stringify(json);
                        Object.defineProperty(self, 'responseText', { get: function() { return modified; }, configurable: true });
                        Object.defineProperty(self, 'response', { get: function() { return modified; }, configurable: true });
                    } catch (e) {}
                }
            });
        }
        return originalSend.apply(this, arguments);
    };

    // =========================================================================
    // 4. Lightweight Master Transparency & OLED Black Style Keeper
    // =========================================================================
    function getMasterCss() {
        return [
            '/* 1. App background pure black, container transparent */',
            'html, body, #app-background {',
            '    background: #000000 !important;',
            '    background-color: #000000 !important;',
            '}',
            '#container {',
            '    background: transparent !important;',
            '    background-color: transparent !important;',
            '}',
            '#loader, .splash-screen-loader {',
            '    background-size: 22% !important;',
            '    background-color: transparent !important;',
            '}',
            '',
            '/* 2. Pure transparent controls, overlays, and scrims without black gradient box */',
            'ytlr-player-controls,',
            'ytlr-control-bar,',
            'ytlr-title-card-renderer,',
            '[class*="control-bar"],',
            '[class*="ControlBar"],',
            '[class*="player-control"],',
            '[class*="PlayerControl"],',
            '[class*="title-card"],',
            '[class*="TitleCard"],',
            '[class*="video-title"],',
            '[class*="VideoTitle"],',
            '[class*="player-overlay"],',
            '[class*="PlayerOverlay"],',
            '.ytp-gradient-bottom,',
            '.ytp-gradient-top,',
            '.ytp-chrome-bottom,',
            '.ytp-chrome-top,',
            '.ytp-chrome-controls,',
            '.ytp-title,',
            '.ytp-title-text,',
            '.ytp-title-channel,',
            '.ytp-tv-controls,',
            '.ytp-bottom-control-flexbox,',
            '.ytp-overlay,',
            '.player-controls,',
            '.player-controls-container,',
            '.ytlr-player-overlay,',
            '.ytp-pause-overlay,',
            '.ytp-player-content,',
            '[class*="gradient"],',
            '[class*="scrim"],',
            '[class*="Vdm04"],',
            '[class*="Vdm04"]:before,',
            '[class*="Vdm04"]:after,',
            '.leUgff,',
            '.YHA8m,',
            '.dwgyh,',
            '.wTHb2c,',
            '.r4Pyib,',
            '.bel0Db,',
            '.q7Ygpb,',
            '.XpH8cb,',
            '.QvTwo,',
            '.jYycK {',
            '    background: transparent !important;',
            '    background-color: transparent !important;',
            '    background-image: none !important;',
            '    box-shadow: none !important;',
            '    border: none !important;',
            '}',
            '',
            '/* 3. Soft shadow for titles and time text on transparent background */',
            '.ytp-title-text, .ytp-title-channel, .ytp-time-display, .ytp-chapter-title-content {',
            '    text-shadow: 0 1px 4px rgba(0,0,0,0.9), 0 0 2px rgba(0,0,0,0.9) !important;',
            '}',
            '',
            '/* 4. Hide large play button overlay on video start */',
            '.ytp-large-play-button,',
            '.ytp-large-play-button-bg,',
            '.ytp-cued-thumbnail-overlay,',
            '.ytp-cued-thumbnail-overlay-image {',
            '    display: none !important;',
            '    opacity: 0 !important;',
            '    pointer-events: none !important;',
            '}',
            '',
            '/* 5. Hide all ad containers, banners, and sponsored cards */',
            '.ad-container, .ytp-ad-overlay-container, .ytp-ad-message-container,',
            '.ytp-ad-progress-list, .video-ads, .ytp-ad-module,',
            '.ytp-ad-player-overlay, .ytp-ad-image-overlay,',
            '.badge-style-type-ad, .badge-shape-wiz--ad,',
            '.ytd-in-feed-ad-layout-renderer, .ytd-promoted-video-renderer,',
            'ytlr-in-feed-ad-renderer, ytlr-ad-slot-renderer, ytlr-promoted-video-renderer,',
            'ytlr-masthead-renderer, ytlr-hero-ad-renderer,',
            '[class*="masthead"], [class*="hero-ad"],',
            'ytd-statement-banner-renderer, ytd-banner-promo-renderer {',
            '    display: none !important;',
            '    visibility: hidden !important;',
            '    height: 0 !important;',
            '    max-height: 0 !important;',
            '    opacity: 0 !important;',
            '    pointer-events: none !important;',
            '}'
        ].join('\n');
    }

    function ensureMasterStyles() {
        var styleId = 'zero-ad-master-style';
        var style = document.getElementById(styleId);
        if (!style) {
            style = document.createElement('style');
            style.id = styleId;
            style.type = 'text/css';
            style.textContent = getMasterCss();
            var target = document.head || document.documentElement;
            if (target) {
                target.appendChild(style);
            }
        }
    }

    ensureMasterStyles();
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', ensureMasterStyles);
    }

    // =========================================================================
    // 5. Zero-Tolerance Instant Ad Killer (Safe 50ms interval)
    // =========================================================================
    function instantAdKiller() {
        var player = document.getElementById('movie_player') || document.querySelector('.html5-video-player');
        var isAd = player && (player.classList.contains('ad-showing') || player.classList.contains('ad-interrupting'));
        var adElement = document.querySelector('.ad-container, .ytp-ad-player-overlay, .video-ads, .ytp-ad-module');

        if (isAd || adElement) {
            var video = document.querySelector('video');
            if (video) {
                try {
                    video.muted = true;
                    if (isFinite(video.duration) && video.duration > 0) {
                        video.currentTime = video.duration;
                        video.playbackRate = 16.0;
                    }
                } catch (e) {}
            }

            // 1. Force skip via official player API
            if (player && typeof player.skipAd === 'function') {
                try { player.skipAd(); } catch (e) {}
            }

            // 2. Click skip button if rendered
            var skipBtn = document.querySelector('.ytp-ad-skip-button, .ytp-ad-skip-button-modern, .ytp-skip-ad-button, .videoAdUiSkipButton');
            if (skipBtn) {
                try { skipBtn.click(); } catch (e) {}
            }
        }

        // Dismiss large play button if present
        var largePlayBtn = document.querySelector('.ytp-large-play-button');
        if (largePlayBtn && largePlayBtn.offsetParent !== null) {
            largePlayBtn.click();
        }

        // Purge sponsored elements in DOM
        var adElements = document.querySelectorAll('ytlr-masthead-renderer, ytlr-in-feed-ad-renderer, ytlr-ad-slot-renderer, [class*="hero-ad"]');
        for (var j = 0; j < adElements.length; j++) {
            adElements[j].remove();
        }
    }

    setInterval(instantAdKiller, 50);

    // =========================================================================
    // 5b. Runtime Scrim Killer + Overlay / Quality Telemetry
    // Catches gradient scrims that arrive via inline <style> or JS-set styles
    // (invisible to the native network interceptor) and reports the real
    // overlay selectors + actual quality ladder to logcat for diagnosis.
    // =========================================================================
    function k2Describe(el) {
        try {
            var c = el.className;
            var cls = (typeof c === 'string') ? c : (c && c.baseVal !== undefined ? String(c.baseVal) : String(c || ''));
            return el.tagName + '.' + cls.split(' ').slice(0, 3).join('.') + '#' + (el.id || '');
        } catch (e) {
            return '?';
        }
    }

    var _k2LastOverlaySig = '';

    function k2ScrimAndTelemetry() {
        try {
            k2EnsureQualityWrap();
            k2UhdMenuMaintenance();
            var sels = [
                '[class*="Vdm04"]', '[class*="scrim"]', '[class*="Scrim"]',
                '[class*="gradient"]', '[class*="Gradient"]',
                '.ytp-gradient-top', '.ytp-gradient-bottom',
                '.ytp-chrome-top', '.ytp-chrome-bottom',
                'ytlr-player-controls', '[class*="control-bar"]', '[class*="ControlBar"]',
                '[class*="title-card"]', '[class*="TitleCard"]',
                '[role="dialog"]', 'dialog'
            ];
            var sigParts = [];
            for (var s = 0; s < sels.length; s++) {
                var els = document.querySelectorAll(sels[s]);
                for (var i = 0; i < els.length; i++) {
                    var r = els[i].getBoundingClientRect();
                    if (r.width <= 0 || r.height <= 0) continue;
                    var cs = window.getComputedStyle(els[i]);
                    if (!cs) continue;
                    var bi = cs.backgroundImage || 'none';
                    var bg = cs.backgroundColor || 'transparent';
                    if (bi && bi !== 'none' && bi.indexOf('gradient') !== -1) {
                        els[i].style.setProperty('background-image', 'none', 'important');
                        els[i].style.setProperty('box-shadow', 'none', 'important');
                        sigParts.push('GRAD-KILLED:' + k2Describe(els[i]));
                    } else if (bg !== 'transparent' && !/rgba\(0,\s*0,\s*0,\s*0\)/.test(bg)) {
                        sigParts.push('BG(' + bg + '):' + k2Describe(els[i]));
                    }
                }
            }
            var sig = sigParts.join(' | ');
            if (sig !== _k2LastOverlaySig) {
                _k2LastOverlaySig = sig;
                console.log('[ZeroAd-Telemetry] overlays: ' + (sig || '(all transparent)'));
            }
        } catch (e) {}
    }

    function k2QualityReport() {
        try {
            var player = document.getElementById('movie_player') || document.querySelector('.html5-video-player');
            var v = document.querySelector('video');
            if (!v || v.paused || v.readyState < 1) return;
            var avail = (player && typeof player.getAvailableQualityLevels === 'function') ? player.getAvailableQualityLevels() : '?';
            var cur = (player && typeof player.getPlaybackQuality === 'function') ? player.getPlaybackQuality() : '?';
            try {
                var vd = (player && typeof player.getVideoData === 'function') ? player.getVideoData() : null;
                var vid = (vd && vd.video_id) ? vd.video_id : '';
                if (vid && vid !== window._k2Vid) { window._k2Vid = vid; window._k2MaxRank = 999; }
                var qr = k2QualityRank(cur);
                var prev = (typeof window._k2MaxRank === 'number') ? window._k2MaxRank : 999;
                if (qr < 999 && qr < prev) window._k2MaxRank = qr;
            } catch (e4) {}
            console.log('[ZeroAd-Telemetry] quality avail=' + JSON.stringify(avail) + ' cur=' + cur +
                ' video=' + v.videoWidth + 'x' + v.videoHeight +
                ' screen=' + window.screen.width + 'x' + window.screen.height +
                ' viewport=' + window.innerWidth + 'x' + window.innerHeight +
                ' dpr=' + window.devicePixelRatio +
                ' qwrap=' + (player && !!player._k2QWrapped) +
                ' lastBrowse=' + (window._k2LastBrowse || '-'));
        } catch (e) {}
    }

    // =========================================================================
    // 5c. Quality-menu UHD restorer.
    // The player DOES play 2160p (settings row shows the 4K badge), but the
    // "current video quality" submenu is built from getAvailableQualityLevels()
    // which stays capped at 1080p. Wrap the API so the menu exposes hd2160 /
    // hd1440 whenever UHD is evidenced (current playback quality or actual
    // decoded frame size). Selecting them works because the formats exist.
    // =========================================================================
    var QUALITY_ORDER = ['hd4320', 'hd2880', 'hd2160', 'hd1440', 'hd1080', 'hd720', 'large', 'medium', 'small', 'tiny'];

    function k2QualityRank(q) {
        var i = QUALITY_ORDER.indexOf(q);
        return i === -1 ? 999 : i;
    }

    function k2MissingHigh(player, have) {
        var out = [];
        try {
            var formats = [];
            try {
                var resp = (player && typeof player.getPlayerResponse === 'function') ? player.getPlayerResponse() : null;
                if (resp && resp.streamingData) {
                    formats = resp.streamingData.adaptiveFormats || [];
                }
            } catch (e0) {}

            var has4320 = false, has2160 = false, has1440 = false, has1080 = false, has720 = false;
            for (var i = 0; i < formats.length; i++) {
                var f = formats[i];
                if (!f) continue;
                var h = f.height || 0;
                var q = (f.quality || '') + (f.qualityLabel || '');
                if (h >= 4320 || q.indexOf('4320') !== -1) has4320 = true;
                if (h >= 2160 || q.indexOf('2160') !== -1) has2160 = true;
                if (h >= 1440 || q.indexOf('1440') !== -1) has1440 = true;
                if (h >= 1080 || q.indexOf('1080') !== -1) has1080 = true;
                if (h >= 720 || q.indexOf('720') !== -1) has720 = true;
            }

            var cur = (player && typeof player.getPlaybackQuality === 'function') ? player.getPlaybackQuality() : '';
            var curRank = k2QualityRank(cur);
            var v = document.querySelector('video');
            var vw = v ? v.videoWidth : 0;
            if (vw >= 7000 || curRank === 0) has4320 = true;
            if (vw >= 3700 || curRank <= 2) has2160 = true;
            if (vw >= 2500 || curRank <= 3) has1440 = true;
            if (vw >= 1800 || curRank <= 4) has1080 = true;
            if (vw >= 1200 || curRank <= 5) has720 = true;

            if (has4320 && !have['hd4320']) out.push('hd4320');
            if (has2160 && !have['hd2160']) out.push('hd2160');
            if (has1440 && !have['hd1440']) out.push('hd1440');
            if (has1080 && !have['hd1080']) out.push('hd1080');
            if (has720 && !have['hd720']) out.push('hd720');
        } catch (e) {}
        return out;
    }

    var _k2LastBoostedVideoId = '';
    function k2AutoBoostQuality(player) {
        if (!player) return;
        try {
            var vData = typeof player.getVideoData === 'function' ? player.getVideoData() : null;
            var vid = vData ? vData.video_id : '';
            if (vid && vid !== _k2LastBoostedVideoId) {
                _k2LastBoostedVideoId = vid;
                player._k2BoostedRank = 999;
            }

            var levels = typeof player.getAvailableQualityLevels === 'function' ? player.getAvailableQualityLevels() : [];
            if (!levels || !levels.length) return;

            // Find highest non-auto quality level
            var highest = null;
            for (var i = 0; i < QUALITY_ORDER.length; i++) {
                var q = QUALITY_ORDER[i];
                if (levels.indexOf(q) !== -1) {
                    highest = q;
                    break;
                }
            }

            if (highest) {
                var hRank = k2QualityRank(highest);
                var cur = typeof player.getPlaybackQuality === 'function' ? player.getPlaybackQuality() : '';
                var curRank = k2QualityRank(cur);

                var lastBoostRank = (typeof player._k2BoostedRank === 'number') ? player._k2BoostedRank : 999;
                if (hRank < lastBoostRank && (curRank > hRank || cur === 'auto' || !cur)) {
                    if (typeof player.setPlaybackQualityRange === 'function') {
                        player.setPlaybackQualityRange(highest, highest);
                    }
                    if (typeof player.setPlaybackQuality === 'function') {
                        player.setPlaybackQuality(highest);
                    }
                    player._k2BoostedRank = hRank;
                    console.log('[ZeroAd] Auto-boosted quality to ' + highest + ' (rank ' + hRank + ', was ' + cur + ', isLive=' + (vData ? vData.isLive : false) + ')');
                } else if (curRank <= hRank && hRank < lastBoostRank) {
                    player._k2BoostedRank = hRank;
                }
            }
        } catch (e) {}
    }

    function k2EnsureQualityWrap() {
        try {
            var player = document.getElementById('movie_player') || document.querySelector('.html5-video-player');
            if (!player) return;

            // Continually monitor and auto-boost quality to the highest available level
            k2AutoBoostQuality(player);

            if (player._k2QWrapped) return;
            var wrappedAny = false;

            if (typeof player.getAvailableQualityLevels === 'function') {
                var _origLevels = player.getAvailableQualityLevels.bind(player);
                player.getAvailableQualityLevels = function() {
                    var list = [];
                    try { list = _origLevels() || []; } catch (e) {}
                    if (!list.length) return list;
                    var have = {};
                    for (var i = 0; i < list.length; i++) have[list[i]] = true;
                    var extra = k2MissingHigh(player, have);
                    var out = list.slice();
                    if (extra.length) {
                        for (var k = 0; k < extra.length; k++) out.push(extra[k]);
                    }
                    var hasAuto = out.indexOf('auto') !== -1;
                    out = out.filter(function(q) { return q !== 'auto'; });
                    out.sort(function(a, b) { return k2QualityRank(a) - k2QualityRank(b); });
                    if (hasAuto) out.push('auto');
                    return out;
                };
                wrappedAny = true;
            }

            if (typeof player.getAvailableQualityData === 'function') {
                var _origData = player.getAvailableQualityData.bind(player);
                player.getAvailableQualityData = function() {
                    var arr = [];
                    try { arr = _origData() || []; } catch (e2) {}
                    if (!arr.length) return arr;
                    try {
                        var have = {}, tpl = null;
                        for (var i = 0; i < arr.length; i++) {
                            var it = arr[i];
                            if (!it || typeof it !== 'object') continue;
                            var sig = '';
                            try { sig = JSON.stringify(it); } catch (e3) { continue; }
                            if (/\b4320\b/.test(sig)) have['hd4320'] = true;
                            if (/\b2160\b/.test(sig)) have['hd2160'] = true;
                            if (/\b1440\b/.test(sig)) have['hd1440'] = true;
                            if (/\b1080\b/.test(sig)) have['hd1080'] = true;
                            if (/\b720\b/.test(sig)) have['hd720'] = true;
                            if (!tpl) tpl = it;
                            if (/\b1080\b/.test(sig) || /\b720\b/.test(sig)) tpl = it;
                        }
                        var extra = k2MissingHigh(player, have);
                        if (extra.length && tpl) {
                            for (var k = 0; k < extra.length; k++) {
                                var qName = extra[k];
                                var num = qName.replace('hd', '');
                                var clone = null;
                                try { clone = JSON.parse(JSON.stringify(tpl)); } catch (e4) {}
                                if (!clone) continue;
                                for (var f in clone) {
                                    if (typeof clone[f] === 'string') {
                                        if (/qual/i.test(f)) clone[f] = qName;
                                        else if (/label/i.test(f)) clone[f] = num + 'p';
                                        else if (/level|name|id/i.test(f)) clone[f] = clone[f].replace(/\d{3,4}/g, num);
                                    } else if (typeof clone[f] === 'number' && /height|qual|level/i.test(f)) {
                                        clone[f] = parseInt(num, 10);
                                    }
                                }
                                arr.push(clone);
                            }
                        }
                        arr.sort(function(a, b) {
                            var qa = (a && (a.quality || a.formatId || '')) || '';
                            var qb = (b && (b.quality || b.formatId || '')) || '';
                            return k2QualityRank(qa) - k2QualityRank(qb);
                        });
                    } catch (e5) {}
                    return arr;
                };
                wrappedAny = true;
            }

            if (wrappedAny) {
                player._k2QWrapped = true;
                console.log('[ZeroAd] quality menu API wrapped for full 8K/4K/HFR exposure.');
            }
        } catch (e) {}
    }

    // Hook video playing event to trigger immediate quality promotion
    document.addEventListener('playing', function(e) {
        if (e.target && e.target.tagName === 'VIDEO') {
            try { k2EnsureQualityWrap(); } catch (err) {}
        }
    }, true);

    // =========================================================================
    // 5d. Back-Navigation & Home Protection
    // Prevents overshooting/redirecting back to the startup account picker screen.
    // =========================================================================
    window._k2LastBrowse = null;
    window._k2InBackNavigation = false;
    window._k2HasLoadedHome = false;

    // Track when user reaches main browsing / watching view
    setInterval(function() {
        try {
            var href = window.location.href || '';
            var hash = window.location.hash || '';
            if (hash.indexOf('browse') !== -1 ||
                href.indexOf('/browse') !== -1 ||
                href.indexOf('/watch') !== -1 ||
                !!document.querySelector('ytlr-browse-feed-renderer, ytlr-channel-view-model, .html5-video-player')) {
                window._k2HasLoadedHome = true;
            }
            if (hash.indexOf('settings') === -1 && href.indexOf('settings') === -1 && !document.querySelector('ytlr-tab-renderer')) {
                window._k2SettingsFirstTabSynced = false;
            }
            k2EnsureQualityWrap();
        } catch (e) {}
    }, 1000);

    // =========================================================================
    // 5e. Quality-submenu spy (READ-ONLY) + DOM-level UHD row injection.
    // NOTE: injection is DISABLED — the app positions rows via JS, so cloned
    // rows stack without coordinates and overlap (broken layout). The menu must
    // be fixed through its data source; this spy reports the real composition.
    // =========================================================================
    var _k2LastMenuSig = '';

    function k2FindQualityMenu() {
        var sels = 'dialog[open], dialog, [role="dialog"], [role="menu"], .ytp-settings-menu, .ytp-popup, .ytp-panel';
        var list = [];
        try { list = document.querySelectorAll(sels); } catch (e) { return null; }
        for (var i = 0; i < list.length; i++) {
            var box = list[i];
            var r = null;
            try { r = box.getBoundingClientRect(); } catch (e2) { continue; }
            if (!r || r.width <= 0 || r.height <= 0) continue;
            var t = '';
            try { t = box.innerText || box.textContent || ''; } catch (e3) {}
            if (/현재 동영상의 화질|Video quality/i.test(t) && /\b1080p\b|\b720p\b/.test(t)) {
                return box;
            }
        }
        return null;
    }

    function k2MenuQualityHave(box) {
        var have = {};
        try {
            var t = box.innerText || box.textContent || '';
            var m = t.match(/\b\d{3,4}p\b/g) || [];
            for (var i = 0; i < m.length; i++) {
                var n = m[i].replace('p', '');
                if (n === '2160') have['hd2160'] = true;
                else if (n === '1440') have['hd1440'] = true;
                else if (n === '1080') have['hd1080'] = true;
                else if (n === '720') have['hd720'] = true;
            }
            if (/\b자동\b|\bAuto\b/.test(t)) have['auto'] = true;
        } catch (e) {}
        return have;
    }

    function k2UhdMenuMaintenance() {
        try {
            var box = k2FindQualityMenu();
            if (!box) return;
            var have = k2MenuQualityHave(box);
            var player = document.getElementById('movie_player') || document.querySelector('.html5-video-player');
            var extra = k2MissingHigh(player, have);
            var names = [];
            for (var k in have) names.push(k);
            var sig = 'items=[' + names.join(',') + '] inject=[' + extra.join(',') + ']';
            if (sig !== _k2LastMenuSig) {
                _k2LastMenuSig = sig;
                console.log('[ZeroAd-Telemetry] qmenu ' + sig);
            }
            if (!extra.length) return;
            // Injection disabled (see 5e banner): cloned rows overlap in the
            // app's JS-positioned list. Keep spy logging above; do not insert.
            return;
            var leaf = null, all = null;
            try { all = box.querySelectorAll('*'); } catch (e) { return; }
            for (var i = 0; i < all.length; i++) {
                var el = all[i];
                if (el.children.length !== 0) continue;
                var tx = '';
                try { tx = (el.innerText || el.textContent || '').trim(); } catch (e2) {}
                if (tx === '1080p' || tx === '1080p HD' || (tx.indexOf('1080p') !== -1 && tx.length <= 12)) { leaf = el; break; }
            }
            if (!leaf) return;
            var row = leaf, p = leaf.parentElement, guard = 0;
            while (p && guard < 4) {
                var pt = '';
                try { pt = (p.innerText || p.textContent || '').trim(); } catch (e3) {}
                if (pt.length > 40) break;
                row = p; p = p.parentElement; guard++;
            }
            var parent = row.parentElement;
            if (!parent) return;
            for (var j = 0; j < extra.length; j++) {
                (function(q) {
                    var label = q.replace('hd', '') + 'p';
                    var clone = row.cloneNode(true);
                    clone.setAttribute('data-k2-uhd', q);
                    clone.removeAttribute('id');
                    var parts = null;
                    try { parts = clone.querySelectorAll('*'); } catch (e4) {}
                    var done = false;
                    if (parts) {
                        for (var s = 0; s < parts.length; s++) {
                            if (parts[s].children.length !== 0) continue;
                            var ot = '';
                            try { ot = (parts[s].innerText || parts[s].textContent || '').trim(); } catch (e5) {}
                            if (ot.indexOf('1080p') !== -1) {
                                parts[s].textContent = ot.replace(/1080p/g, label);
                                done = true;
                            }
                        }
                    }
                    if (!done) {
                        try { clone.textContent = label; } catch (e6) {}
                    }
                    clone.addEventListener('click', function(ev) {
                        try { ev.stopPropagation(); } catch (e7) {}
                        try {
                            var pl = document.getElementById('movie_player') || document.querySelector('.html5-video-player');
                            if (pl && typeof pl.setPlaybackQuality === 'function') {
                                pl.setPlaybackQuality(q);
                                console.log('[ZeroAd] UHD menu row selected: ' + q);
                            }
                        } catch (e8) {}
                    }, true);
                    try { parent.insertBefore(clone, parent.firstChild); } catch (e9) { return; }
                })(extra[j]);
            }
        } catch (e) {}
    }

    setInterval(k2ScrimAndTelemetry, 2000);
    setInterval(k2QualityReport, 10000);

    // =========================================================================
    // 6. Starboard / Cobalt H5VCC Polyfill Interface
    // =========================================================================
    if (!window.h5vcc) {
        var serviceCallbacks = {};
        var nextServiceId = 1;

        window._onPlatformServiceReceive = function(serviceId, jsonString) {
            if (serviceCallbacks[serviceId]) {
                try {
                    serviceCallbacks[serviceId](jsonString);
                } catch (e) {}
            }
        };

        window.h5vcc = {
            system: {
                get buildFingerprint() {
                    return (window.NativeBridge && window.NativeBridge.getBuildFingerprint()) || "google/chromecast/eureka:12/STTE.231215.005/11324838:user/release-keys";
                },
                get hardwareType() { return 1; },
                get deviceYear() { return 2024; },
                get chipsetModelNumber() {
                    return (window.NativeBridge && window.NativeBridge.getChipset()) || "Amlogic S905X4";
                },
                get areSystemNotificationCardsEnabled() { return false; },
                get certificationScope() { return "sagit"; }
            },
            storage: {
                clear: function() { if (window.NativeBridge) window.NativeBridge.storageClear(); },
                flush: function() { if (window.NativeBridge) window.NativeBridge.storageFlush(); }
            },
            settings: { isMediaPlaybackDisabled: false },
            runtime: { initialDeepLink: "" },
            platformService: {
                has: function(serviceName) { return true; },
                open: function(serviceName, callback) {
                    var serviceId = 0;
                    if (window.NativeBridge) {
                        serviceId = window.NativeBridge.openPlatformService(serviceName);
                    } else {
                        serviceId = nextServiceId++;
                    }

                    serviceCallbacks[serviceId] = callback;

                    return {
                        send: function(data) {
                            if (window.NativeBridge) {
                                window.NativeBridge.sendPlatformService(serviceId, data);
                            }
                        },
                        close: function() {
                            if (window.NativeBridge) {
                                window.NativeBridge.closePlatformService(serviceId);
                            }
                            delete serviceCallbacks[serviceId];
                        }
                    };
                }
            }
        };
    }

    // =========================================================================
    // 7. YouTube TV Settings Screen Update Widget Injector & Premium Purger
    // - Hides 'YouTube Premium 가입' from the top of settings
    // - Injects a dedicated '최신 앱 업데이트 확인' tab right above '앱 버전'
    // - Completely separates active/focus states and right detail panel
    // =========================================================================
    function k2SetElementFocusState(tabEl, focused) {
        if (!tabEl) return;
        var btn = tabEl.querySelector('ytlr-button');
        var lockup = tabEl.querySelector('ytlr-avatar-lockup');
        if (focused) {
            tabEl.classList.add('V0Tdtb', 'qzhmA', 'zylon-focus');
            tabEl.classList.remove('JqwODe');
            if (btn) {
                btn.classList.add('BZ345e', 'zylon-focus');
                btn.classList.remove('pAenK');
            }
            if (lockup) {
                lockup.classList.add('dalgG');
                lockup.classList.remove('yZD8Ze');
            }
        } else {
            tabEl.classList.remove('V0Tdtb', 'qzhmA', 'zylon-focus');
            tabEl.classList.add('JqwODe');
            if (btn) {
                btn.classList.remove('BZ345e', 'zylon-focus');
                btn.classList.add('pAenK');
            }
            if (lockup) {
                lockup.classList.remove('dalgG');
                lockup.classList.add('yZD8Ze');
            }
        }
    }

    function k2UpdateRightDetailPanel(isUpdateTabFocused) {
        try {
            var scrollPane = document.querySelector('yt-scroll-pane');
            if (!scrollPane) return;
            var origBox = scrollPane.querySelector('.ogHbMc');
            var customId = 'yt-ac-update-detail-panel';
            var customPanel = document.getElementById(customId);

            if (isUpdateTabFocused) {
                if (origBox) origBox.style.display = 'none';
                if (!customPanel) {
                    customPanel = document.createElement('div');
                    customPanel.id = customId;
                    customPanel.className = 'ogHbMc';
                    customPanel.innerHTML =
                        '<div class="WBbfC" style="padding-top: 0rem; padding-right: 1.84rem;">' +
                        '<div class="XMA1jc"><div class="vjkzh">업데이트 검사</div><div class="LNwekb">리모컨 선택(확인) 시 최신 빌드를 즉시 확인합니다</div></div>' +
                        '<div class="XMA1jc"><div class="vjkzh">배포 방식</div><div class="LNwekb">GitHub OTA 원클릭 자동/수동 업데이트</div></div>' +
                        '<div class="XMA1jc"><div class="vjkzh">엔진 상태</div><div class="LNwekb">Zero-Ad 무광고 클린 엔진 & 4K 복원 활성화</div></div>' +
                        '</div>';
                    scrollPane.appendChild(customPanel);
                }
                customPanel.style.display = 'block';
            } else {
                if (customPanel) customPanel.style.display = 'none';
                if (origBox) origBox.style.display = '';
            }
        } catch (e) {}
    }

    function k2SetupGlobalKeyHandler() {
        if (window._k2GlobalKeySetup) return;
        window._k2GlobalKeySetup = true;

        window.addEventListener('keydown', function(e) {
            // Ignore key repeats: holding DOWN/UP must fast-scroll natively.
            // Re-firing focus jumps + .click() on every repeat ejects focus
            // out of the settings list (e.g. all the way to the Shorts rail).
            if (e.repeat) return;
            var myTab = document.getElementById('yt-ac-settings-update-banner');
            if (!myTab) return;

            var allTabs = Array.from(document.querySelectorAll('ytlr-tab-renderer'));
            var versionTab = allTabs.find(function(t) {
                return t.id !== 'yt-ac-settings-update-banner' && /(앱\s*버전|App\s*version)/i.test(t.innerText);
            });
            if (!versionTab) return;

            var active = document.activeElement;
            var isMyTabActive = myTab.contains(active);
            var isVersionActive = versionTab.contains(active);

            // Find the terms tab (previous tab)
            var termsTab = allTabs.find(function(t) { return /개인정보|약관|Terms/i.test(t.innerText); });
            var isTermsActive = termsTab && termsTab.contains(active);

            var isDown = (e.keyCode === 40 || e.keyCode === 20 || e.key === 'ArrowDown' || e.key === 'Down');
            var isUp = (e.keyCode === 38 || e.keyCode === 19 || e.key === 'ArrowUp' || e.key === 'Up');
            var isEnter = (e.keyCode === 13 || e.keyCode === 23 || e.key === 'Enter');

            // 1. If currently on Terms tab and presses DOWN -> jump to update tab
            if (isTermsActive && isDown) {
                e.preventDefault();
                e.stopPropagation();
                var uBtn = myTab.querySelector('ytlr-button') || myTab;
                if (termsTab) k2SetElementFocusState(termsTab, false);
                k2SetElementFocusState(versionTab, false);
                k2SetElementFocusState(myTab, true);
                k2UpdateRightDetailPanel(true);
                uBtn.focus();
                return;
            }

            // 2. If currently on Update tab:
            if (isMyTabActive) {
                if (isEnter) {
                    e.preventDefault();
                    e.stopPropagation();
                    if (window.YT_TV_APP && typeof window.YT_TV_APP.checkAppUpdate === 'function') {
                        window.YT_TV_APP.checkAppUpdate();
                    }
                    return;
                }
                if (isUp) {
                    e.preventDefault();
                    e.stopPropagation();
                    k2SetElementFocusState(myTab, false);
                    k2UpdateRightDetailPanel(false);
                    if (termsTab) {
                        var tBtn = termsTab.querySelector('ytlr-button') || termsTab;
                        tBtn.focus();
                        tBtn.click();
                    }
                    return;
                }
                if (isDown) {
                    e.preventDefault();
                    e.stopPropagation();
                    k2SetElementFocusState(myTab, false);
                    k2SetElementFocusState(versionTab, true);
                    k2UpdateRightDetailPanel(false);
                    var vBtn = versionTab.querySelector('ytlr-button') || versionTab;
                    vBtn.focus();
                    vBtn.click();
                    return;
                }
            }

            // 3. If currently on Version tab and presses UP -> jump to update tab
            if (isVersionActive && isUp) {
                e.preventDefault();
                e.stopPropagation();
                var uBtn2 = myTab.querySelector('ytlr-button') || myTab;
                k2SetElementFocusState(versionTab, false);
                k2SetElementFocusState(myTab, true);
                k2UpdateRightDetailPanel(true);
                uBtn2.focus();
                return;
            }
        }, true);
    }

    // GitHub repo QR for Settings > About > Help Center (replaces youtube.com/tv_help QR).
    var K2_GITHUB_URL_TEXT = 'github.com/k2love/YT_AC';
    var K2_GITHUB_PULLS_URL_TEXT = 'github.com/k2love/YT_AC/pulls';
    var K2_GITHUB_PULLS_QR_DATA_URL = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAgQAAAIECAYAAABmAjaWAAALu0lEQVR4nO3dAYrrSAxFUXvI/rfs4WsBA8VE30/ROQtonIqdvphCdT/P81wAwGr/vH0BAMD7BAEAIAgAAEEAAAgCAEAQAADFpkIAQBAAAIIAABAEAIAgAACKTYUAgCAAAAQBACAIAABBAAAUmwoBAEEAAAgCAEAQAACCAAAoNhUCAIIAABAEAIAgAAAEAQBQbCoEAAQBACAIAABBAAAIAgCg2FQIAAgCAEAQAACCAAD445O2DPd9v30JP+V5nmvy93t6/dv+PrOel+7vd/r1b/OE/T7bVAgACAIAQBAAAIIAABAEAECxqRAAEAQAgCAAAAQBACAIAIBiUyEAkHeWwfRZ0N26Z4mnzVqffnZA9/VPv55uabP3t32/0++f6ffbKW8IAABBAAAIAgBAEAAAggAAKDYVAgCCAAAQBACAIAAABAEAUGwqBADmn2UwfdZ02qzvtFnr3X8/7eyDbZ837Xq6pa1nmrTv9xm+nqe8IQAABAEAIAgAAEEAAAgCAKDYVAgACAIAQBAAAIIAABAEAECxqRAA2HeWAe/qnl2fNnu8+3qmnwWQdj1ptj0vvMsbAgBAEAAAggAAEAQAgCAAAIpNhQCAIAAABAEAIAgAAEEAABSbCgEAZxnw/2ybnZ52/d1nAaSdldC9/mlnK2x7vniXNwQAgCAAAAQBACAIAABBAAAUmwoBAEEAAAgCAEAQAACCAAAoNhUCAPvOMjDr+7dnp3df//RZ/Wl//3Q909Z/+vWkPb9p17ONNwQAgCAAAAQBACAIAABBAAAUmwoBAEEAAAgCAEAQAACCAAAoNhUCAPPPMuieJc53TT9rYPosen9/1vpMt+3zTucNAQAgCAAAQQAACAIAQBAAAMWmQgBAEAAAggAAEAQAgCAAAIpNhQBA3lkGp7PB+W3ds9C7Z9dvmxXfvT5p65/G+vN/eEMAAAgCAEAQAACCAAAQBABAsakQABAEAIAgAAAEAQAgCACAYlMhAHDdj+HgPz1b/lT37dB9dkDa+qetZ5q09XG/fXc9T6X9O7qHn3VyyhsCAEAQAACCAAAQBACAIAAAik2FAIAgAAAEAQAgCAAAQQAAFJsKAYDrM30N0ma5p82yPl2ftPXcNou+W/f6bFv/6c/79Os/dfp5n7D16eYNAQAgCAAAQQAACAIAQBAAAMWmQgBAEAAAggAAEAQAgCAAAIpNhQBA3lkGabPNu2dZp83unv59nZo+q3z62QRp6592P6c9v2lnVWy7P7t5QwAACAIAQBAAAIIAABAEAECxqRAAEAQAgCAAAAQBACAIAIBiUyEAkHeWAb89WzttFvqptFno02fRp33etO/rVNr3O/336g573rt5QwAACAIAQBAAAIIAABAEAECxqRAAEAQAgCAAAAQBACAIAIBiUyEA4CyDb+ueDZ42W3767O609dx2/2ybFZ921sApZx/8Nm8IAABBAAAIAgBAEAAAggAAKDYVAgCCAAAQBACAIAAABAEAUGwqBACu+5k+HLzZttnd0z+v6393/ad/X91nK6T9/VPbrucJe166eUMAAAgCAEAQAACCAAAQBABAsakQABAEAIAgAAAEAQAgCACAYlMhAHB90tYgbdZ02uzutPU51b0+aabPrk+z7X6efhbA9OvZxhsCAEAQAACCAAAQBACAIAAAik2FAIAgAAAEAQAgCAAAQQAAFJsKAYDrftKGgy+TNuu++3aYPns87XHZdv+c2jZ7P+16Tk3//XnC7v9T3hAAAIIAABAEAIAgAAAEAQBQbCoEAAQBACAIAABBAAAIAgCg2FQIAFyfbWuQNvv9VNrs8bTrmT5LPO3+TPv70++HtOuZLu335w67/095QwAACAIAQBAAAIIAABAEAECxqRAAEAQAgCAAAAQBACAIAIBiUyEAkHeWQfcs6LTZ7Gmzr9M+73Tb1jNtNnu3tPU/lfZ7kva8PMvuZ28IAABBAAAIAgBAEAAAggAAKDYVAgCCAAAQBACAIAAABAEAUGwqBACu+xk+rDltNvX02eZ8V9qs9e77c/r1pJn++5Z2P2y7f055QwAACAIAQBAAAIIAABAEAECxqRAAEAQAgCAAAAQBACAIAIBiUyEAcH2mr0HarOnps+vT1nP69W+TdjbB9OvZdj+nncWwjTcEAIAgAAAEAQAgCAAAQQAAFJsKAQBBAAAIAgBAEAAAggAAKDYVAgDX/Qwflr1tVnna5+227fNOl3b/T3++tn3ebWcTPGG/P94QAACCAAAQBACAIAAABAEAUGwqBAAEAQAgCAAAQQAACAIAoNhUCABcn7Q12DZLfPps8LRZ3NO/37TZ7Ns+76m0swOmm74+T9jv4SlvCAAAQQAACAIAQBAAAIIAACg2FQIAggAAEAQAgCAAAAQBAFBsKgQArvsZPnzZLPrfnl2fdj3Tz1YwK/67tq1n2vPLd3lDAAAIAgBAEAAAggAAEAQAQLGpEAAQBACAIAAABAEAIAgAgGJTIQAw/yyDU2Zxv7s+aWcHbFvPbWdDnHL97/L9vssbAgBAEAAAggAAEAQAgCAAAIpNhQCAIAAABAEAIAgAAEEAABSbCgGA6zN9DabPiu+end4tbX3Srift76eZPru+W9r1p91vaWdP3MOfX28IAABBAAAIAgBAEAAAggAAKDYVAgCCAAAQBACAIAAABAEAUGwqBADyzjLonk2dNms6bZb79LMGuqVdz6np6592/dvu/7TfkzRP2Pd1yhsCAEAQAACCAAAQBACAIAAAik2FAIAgAAAEAQAgCAAAQQAAFJsKAYC8swymz4JOm8WdNkt8+vc7Xdr9MH22/7azA9LOdkn7vZ3OGwIAQBAAAIIAABAEAIAgAACKTYUAgCAAAAQBACAIAABBAAAUmwoBgOt+lg0HT5vd3W36rO/ps83TZstbH+vv/snxhP1/8YYAABAEAIAgAAAEAQAgCACAYlMhACAIAABBAAAIAgBAEAAAxaZCACDvLIO0Weunps+WP+XzzjqboPtx33Y/p5m+/qfSnpc77Hk85Q0BACAIAABBAAAIAgBAEAAAxaZCAEAQAACCAAAQBACAIAAAik2FAEDeWQb89iz0bWcfpEmbzZ72/W476yHt53/6788Ttp6nvCEAAAQBACAIAABBAAAIAgCg2FQIAAgCAEAQAACCAAAQBABAsakQALg+aWuQNut7uu7Z2mmzwaffP2mfN+16ulnP357tP/36u3lDAAAIAgBAEAAAggAAEAQAQLGpEAAQBACAIAAABAEAIAgAgGJTIQCQd5bBqW2zpqfPit92P5x+X9NnrXdfT9pZGNP//qnp95vfz//mDQEAIAgAAEEAAAgCAEAQAADFpkIAQBAAAIIAABAEAIAgAACKTYUAwPyzDE6lzbJOmw3eLW32+6lts+Knr0/a/ZMm7fdw2/Wn8YYAABAEAIAgAAAEAQAgCACAYlMhACAIAABBAAAIAgBAEAAAxaZCAGDfWQb8N7Piv7s+088CSPv7affztufL+vw2bwgAAEEAAAgCAEAQAACCAAAoNhUCAIIAABAEAIAgAAAEAQBQbCoEAJxlwN/VPQt926z17s+bZtvnZdbz8oSd5XHKGwIAQBAAAIIAABAEAIAgAACKTYUAgCAAAAQBACAIAABBAAAUmwoBgH1nGUyfNc27s827zyY41f330z5vt7T17Jb2/aZdzzbeEAAAggAAEAQAgCAAAAQBAFBsKgQABAEAIAgAAEEAAAgCAKDYVAgAzD/LIG02+DbdZwdMvx+6r8dZCd9llj6b7x9vCAAAQQAACAIAQBAAAIIAACg2FQIAggAAEAQAgCAAAAQBAFBsKgQArvtJG6YMAPx13hAAAIIAABAEAIAgAAAEAQBQbCoEAAQBACAIAABBAAAIAgCg2FQIAAgCAEAQAACCAAAQBABAsakQABAEAIAgAAAEAQAgCACAYlMhACAIAABBAAAIAgBAEAAAxaZCAEAQAACCAAAQBACAIAAAik2FAIAgAAAEAQAgCAAAQQAAXH/8C/EwrzkdaBjnAAAAAElFTkSuQmCC';
    var K2_GITHUB_QR_DATA_URL = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAdQAAAHUCAYAAACDJ9lsAAAKwElEQVR4nO3cQY4jORJFwdSg7n/lmBs0OlCPne6i2bonEaJC9cBZ/M/zPM8PAPBX/vd3/3MAQFABIOKGCgABQQWAgKACQEBQASAgqAAQEFQACAgqAAQEFQACggoAAUEFgICgAkBAUAEgIKgAEBBUAAgIKgAEBBUAAoIKAAFBBYCAoAJAQFABICCoABAQVAAICCoABAQVAAKCCgABQQWAgKACQEBQASAgqAAQEFQACAgqAAQEFQAEFQBm+PMzzOfz+e1H+CrP84w6/7fPc9q0zzvt/T/9fU37vLd9v9s9w/498X/5AkBAUAEgIKgAEBBUAAgIKgAEBBUAAoIKAAFBBYCAoAJAQFABICCoAPCNW77btxxv2569zenzmbad+/a/f/v807Zwp73/057ntM/yrWM3VAAICCoABAQVAAKCCgABQQWAgKACQEBQASAgqAAQEFQACAgqAAQEFQAC67d8t29F3rbVOY3zb8/n9Pbvabc9/2nPsPM5zQ0VAAKCCgABQQWAgKACQEBQASAgqAAQEFQACAgqAAQEFQAEFQBmcEMFgMB1W7787hbo6W3YabZvmTp/+PfcUAEgIKgAEBBUAAgIKgAEBBUAAoIKAAFBBYCAoAJAQFABICCoABAQVAAI2PLlq7Z2p23nvj2faec/7XlgMjdUAAgIKgAEBBUAAoIKAAFBBYCAoAJAQFABICCoABAQVAAICCoABAQVAALXbflO23rd7vTW67Qt2bfPc/p9m/Y+T3ue2zj/3+WGCgABQQWAgKACQEBQASAgqAAQEFQACAgqAAQEFQAEFQBmcEMFgICgAkBg/Zbv6e3W25ze2p1m+xbxbX//tGnP79+3XdxQASAgqAAQEFQACAgqAAQEFQACggoAAUEFgICgAkBAUAEgIKgAEBBUAAh8nmljmny109uk017n2z7vbdu528+flhsqAAQEFQACggoAAUEFgICgAkBAUAEgIKgAEBBUAAgIKgAEBBUAAoIKAIE/P5c5vdV5erv1rdPP//bvn36ead/vbVuv095/78Pvns/253nLDRUAAoIKAAFBBYCAoAJAQFABICCoABAQVAAICCoABAQVAAKCCgABQQWAb9zyPb0FOm370TbmrvPcvu381rSt5rembTVP26qd9n1t54YKAAFBBYCAoAJAQFABICCoABAQVAAICCoABAQVAAKCCgABQQWAgKACQODzTBu3fWna9uY02z/vtNdz2vs27XxOcz7t+Wz3DHv/3VABICCoABAQVAAICCoABAQVAAKCCgABQQWAgKACQEBQASAgqAAQEFQACPz5WW7aVuptW6PTtoJvO//tn3fa9uzp5zl9/tv/vfoMex/eckMFgICgAkBAUAEgIKgAEBBUAAgIKgAEBBUAAoIKAAFBBYCAoAJAQFABIPB5ho17bt9ynGba9ub2rdG3nM/vnud2238vn+XbyG+5oQJAQFABICCoABAQVAAICCoABAQVAAKCCgABQQWAgKACQEBQASAgqAAQ+PNz2XblW9O2Lqedz/bPu/3vn7b99zVt63XaeU5737ZzQwWAgKACQEBQASAgqAAQEFQACAgqAAQEFQACggoAAUEFgICgAkBAUAHgG7d8p21dnjZte3Pa80zbzp3299+att26/Xxuex7+mRsqAAQEFQACggoAAUEFgICgAkBAUAEgIKgAEBBUAAgIKgAEBBUAAoIKAN+45XvbNua055lm2nbutC3c06adz+nvd9rnnfb+n/ZZ/vtyQwWAgKACQEBQASAgqAAQEFQACAgqAAQEFQACggoAAUEFgICgAkBAUAHgG7d8p211TjNtO5T2PKe9/9u3Vbe7bZv6Wf7vjxsqAAQEFQACggoAAUEFgICgAkBAUAEgIKgAEBBUAAgIKgAEBBUAAoIKAN+45Ttt63Ka257/tu/3tO3bsL7fXZ7Lfo9uqAAQEFQACAgqAAQEFQACggoAAUEFgICgAkBAUAEgIKgAEBBUAAgIKgAE1m/5TnN6y3Tatu20rc5p5/PWtOd56/T277Tvd9rW8fbva/vvxQ0VAAKCCgABQQWAgKACQEBQASAgqAAQEFQACAgqAAQEFQACggoAAUEFgMB1W77TtjS3b1ee3lY9/XlPP/+07dnTtv++btvO3f57nMYNFQACggoAAUEFgICgAkBAUAEgIKgAEBBUAAgIKgAEBBUAAoIKAAFBBYDA5xk2Hnp6y/H0liat7duh259/mtvOc9rntWX9z9xQASAgqAAQEFQACAgqAAQEFQACggoAAUEFgICgAkBAUAEgIKgAEBBUAAj8+Rlm+3blNNu3am9jS/Z3z9NWbXuet/377IYKAAFBBYCAoAJAQFABICCoABAQVAAICCoABAQVAAKCCgABQQWAgKACwDdu+Z7ecjy91TnN9s877X2YZtrzT9tinfb3p20L03JDBYCAoAJAQFABICCoABAQVAAICCoABAQVAAKCCgABQQWAgKACQEBQAeAbt3xv2648vTV6+nymbbe+NW1bddr7sH0re/t5vjXt9/XW9n/P3VABICCoABAQVAAICCoABAQVAAKCCgABQQWAgKACQEBQASAgqAAQEFQA+MYt32nbqtN4/l2mvZ/TnmeaadvX02zfsj7NDRUAAoIKAAFBBYCAoAJAQFABICCoABAQVAAICCoABAQVAAKCCgABQQWAwOfZPp7IV2+Nbn89p53nbd/XtG3k027bQn+Gnb8bKgAEBBUAAoIKAAFBBYCAoAJAQFABICCoABAQVAAICCoABAQVAAKCCgCBPz/DTNuK3O7t1uW0bcxpW6zTtlJ9X7tM+36nvc/buaECQEBQASAgqAAQEFQACAgqAAQEFQACggoAAUEFgICgAkBAUAEgIKgA8I1bvm9N2zI97fQ25rTt3Gnboafft2nbradNO8/t789bt53/aW6oABAQVAAICCoABAQVAAKCCgABQQWAgKACQEBQASAgqAAQEFQACAgqAATWb/m+NW0rctq25/atzu3P89bb55/2PNvd9nm3v5+nuaECQEBQASAgqAAQEFQACAgqAAQEFQACggoAAUEFgICgAkBAUAEgIKgAELhuy5ff3dKcttV5evt32tbr6W3Vad/vbVuy0963Z/l5vuWGCgABQQWAgKACQEBQASAgqAAQEFQACAgqAAQEFQACggoAAUEFgICgAkDAli//6Rbo9m3Pac8/bbv1ts97eivY5931e3RDBYCAoAJAQFABICCoABAQVAAICCoABAQVAAKCCgABQQWAgKACQEBQASBw3ZbvtO3HaaZtjU7bFp72PNPe59Pbtqdtf/7Tz3P69/IMO8+33FABICCoABAQVAAICCoABAQVAAKCCgABQQWAgKACQEBQASAgqAAQEFQACKzf8j29rQr/5dbotK3g039/++932vNPe563tm//uqECQEBQASAgqAAQEFQACAgqAAQEFQACggoAAUEFgICgAkBAUAEgIKgAEPg808YQAWAhN1QACAgqAAQEFQACggoAAUEFgICgAkBAUAEgIKgAEBBUAAgIKgAEBBUAAoIKAAFBBYCAoAJAQFABICCoABAQVAAICCoABAQVAAKCCgABQQWAgKACQEBQASAgqAAQEFQACAgqAAQEFQACggoAAUEFgICgAkBAUAEgIKgAEBBUAAgIKgAEBBUAfv7e/wHef/6aKA8AWgAAAABJRU5ErkJggg==';

    // Patches ONLY the Help Center right panel ([idomkey="AboutSettingItemIdABOUT_HELP"]):
    // swaps the QR background to the GitHub repo QR and rewrites the help URL text.
    // Strictly scoped - 'Send feedback' (의견 보내기) and all other panels untouched.
    // Tag-agnostic text replacement inside a scope (a URL may live in a plain
    // DIV/SPAN, not only yt-formatted-string). Layout-safe: only text node
    // values change, no elements are added or restyled.
    function k2ReplaceTextIn(scope, from, to) {
        try {
            var walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT, null);
            var nodes = [], nd = null;
            while ((nd = walker.nextNode())) nodes.push(nd);
            for (var i = 0; i < nodes.length; i++) {
                var v = nodes[i].nodeValue;
                if (v && v.indexOf(from) !== -1) nodes[i].nodeValue = v.split(from).join(to);
            }
        } catch (e) {}
    }

    function k2PatchHelpCenterPanel() {
        try {
            var panels = document.querySelectorAll('[idomkey="AboutSettingItemIdABOUT_HELP"]');
            if (!panels.length) return;

            for (var pi = 0; pi < panels.length; pi++) {
            var panel = panels[pi];
            // 1. QR code background (ytlr-thumbnail-details holds style.backgroundImage = url(...))
            var thumbs = panel.querySelectorAll('ytlr-thumbnail-details');
            for (var i = 0; i < thumbs.length; i++) {
                var el = thumbs[i];
                var current = '';
                try { current = el.style.backgroundImage || ''; } catch (e0) {}
                if (!current) {
                    try {
                        var cs = window.getComputedStyle(el);
                        if (cs) current = cs.backgroundImage || '';
                    } catch (e1) {}
                }
                if (current && current.indexOf('data:image') !== -1 &&
                    current.indexOf(K2_GITHUB_QR_DATA_URL) === -1) {
                    el.style.setProperty('background-image', 'url("' + K2_GITHUB_QR_DATA_URL + '")', 'important');
                    if (!window._k2HelpLogged) {
                        console.log('[ZeroAd] Help Center QR replaced with GitHub repo QR.');
                    }
                }
            }

            // 2. Help URL text (youtube.com/tv_help -> github.com/k2love/YT_AC).
            // Tag-agnostic via text-node walker: the URL may sit in a DIV/SPAN.
            (function() {
                var had = false;
                try { had = (panel.textContent || '').indexOf('youtube.com/tv_help') !== -1; } catch (e9) {}
                k2ReplaceTextIn(panel, 'youtube.com/tv_help', K2_GITHUB_URL_TEXT);
                if (had && !window._k2HelpLogged) {
                    console.log('[ZeroAd] Help Center URL replaced with GitHub repo URL.');
                }
            })();
            } // panels loop

            window._k2HelpLogged = true;
        } catch (e) {
            console.warn('[ZeroAd] Error patching help center panel:', e);
        }
    }

    function k2InjectSettingsUpdateCard() {
        try {
            k2SetupGlobalKeyHandler();

            // Find all ytlr-tab-renderer elements in settings list
            var allTabs = Array.from(document.querySelectorAll('ytlr-tab-renderer'));
            if (allTabs.length === 0) return;

            // 1. Hide 'YouTube Premium 가입' tab if present & purge right-side premium action renderer
            var premiumTab = null;
            for (var p = 0; p < allTabs.length; p++) {
                var tab = allTabs[p];
                var txt = (tab.innerText || tab.textContent || '').trim();
                if (/Premium|프리미엄/i.test(txt)) {
                    premiumTab = tab;
                    if (tab.style.display !== 'none') {
                        tab.style.setProperty('display', 'none', 'important');
                        tab.setAttribute('aria-hidden', 'true');
                        tab.removeAttribute('hybridnavfocusable');
                    }
                }
            }

            // Also purge right detail panel if it contains YouTube Premium upsell
            var premiumRightRenderer = document.querySelector('ytlr-setting-action-renderer');
            var hasPremiumOnRight = false;
            if (premiumRightRenderer) {
                var rTxt = (premiumRightRenderer.innerText || '').trim();
                if (/Premium|프리미엄/i.test(rTxt)) {
                    hasPremiumOnRight = true;
                    premiumRightRenderer.style.setProperty('display', 'none', 'important');
                }
            }

            // If premium was active or is lingering on the right screen, auto-select the first valid tab
            var firstTab = allTabs.find(function(t) {
                return t.style.display !== 'none' && t !== premiumTab && t.id !== 'section-header:z1' && !t.classList.contains('EtB6Qe') && t.id !== 'yt-ac-settings-update-banner';
            });

            if (firstTab) {
                var isPremiumFocused = premiumTab && (premiumTab.classList.contains('zylon-focus') || premiumTab.classList.contains('V0Tdtb'));
                if (isPremiumFocused || hasPremiumOnRight || !window._k2SettingsFirstTabSynced) {
                    window._k2SettingsFirstTabSynced = true;
                    if (premiumTab) k2SetElementFocusState(premiumTab, false);
                    var fBtn = firstTab.querySelector('ytlr-button') || firstTab;
                    try {
                        fBtn.click();
                        firstTab.click();
                    } catch (e) {}
                }
            }

            var existingTab = document.getElementById('yt-ac-settings-update-banner');

            var versionTab = allTabs.find(function(t) {
                if (t.id === 'yt-ac-settings-update-banner') return false;
                var txt = (t.innerText || '').trim();
                return txt.includes('앱 버전') || txt.includes('App version') || txt.includes('버전');
            });

            if (!versionTab || !versionTab.parentElement) return;

            function focusUpdateTab(targetTab) {
                var activeTab = targetTab || existingTab;
                if (!activeTab) return;
                var prev = activeTab.previousElementSibling;
                if (prev) k2SetElementFocusState(prev, false);
                k2SetElementFocusState(versionTab, false);
                k2SetElementFocusState(activeTab, true);
                k2UpdateRightDetailPanel(true);
                var uBtn = activeTab.querySelector('ytlr-button') || activeTab;
                uBtn.focus();
            }

            function unfocusUpdateTab(targetTab) {
                var activeTab = targetTab || existingTab;
                if (activeTab) k2SetElementFocusState(activeTab, false);
                k2UpdateRightDetailPanel(false);
            }

            // If already injected and correctly placed right before versionTab, check focus sync
            if (existingTab) {
                if (existingTab.nextElementSibling !== versionTab && existingTab !== versionTab) {
                    versionTab.parentElement.insertBefore(existingTab, versionTab);
                }

                // Check if update tab has focus
                var isUpdateActive = existingTab.matches(':focus') || existingTab.querySelector(':focus') !== null;
                var isVersionActive = versionTab.matches(':focus') || versionTab.querySelector(':focus') !== null;

                if (isUpdateActive && !isVersionActive) {
                    k2SetElementFocusState(existingTab, true);
                    k2SetElementFocusState(versionTab, false);
                    k2UpdateRightDetailPanel(true);
                } else if (isVersionActive && !isUpdateActive) {
                    k2SetElementFocusState(existingTab, false);
                    k2SetElementFocusState(versionTab, true);
                    k2UpdateRightDetailPanel(false);
                } else if (!isUpdateActive) {
                    // Make sure update tab doesn't accidentally retain focus class
                    if (existingTab.classList.contains('zylon-focus')) {
                        k2SetElementFocusState(existingTab, false);
                    }
                }
                return;
            }

            // Clone versionTab to inherit 100% of YouTube TV's native layout, fonts, and styling
            var myTab = versionTab.cloneNode(true);
            myTab.id = 'yt-ac-settings-update-banner';
            myTab.removeAttribute('idomkey');
            myTab.removeAttribute('aria-labelledby');
            myTab.removeAttribute('aria-selected');
            myTab.tabIndex = 0;

            // Initialize to clean unselected state immediately!
            k2SetElementFocusState(myTab, false);

            // Update text to pure plain text matching native menu exactly (no emoji!)
            var textEl = myTab.querySelector('yt-formatted-string') || myTab.querySelector('span') || myTab;
            textEl.textContent = '최신 앱 업데이트 확인';

            function triggerCheck(e) {
                if (e) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                console.log('[ZeroAd] Settings update button activated.');
                if (window.YT_TV_APP && typeof window.YT_TV_APP.checkAppUpdate === 'function') {
                    window.YT_TV_APP.checkAppUpdate();
                }
            }

            // Remote D-Pad Navigation & Focus Handlers
            var btn = myTab.querySelector('ytlr-button') || myTab;
            btn.tabIndex = 0;

            myTab.addEventListener('focusin', function() {
                focusUpdateTab(myTab);
            });

            myTab.addEventListener('focusout', function(e) {
                if (!myTab.contains(e.relatedTarget)) {
                    unfocusUpdateTab(myTab);
                }
            });

            versionTab.addEventListener('focusin', function() {
                unfocusUpdateTab(myTab);
                k2SetElementFocusState(versionTab, true);
            });

            versionTab.addEventListener('click', function() {
                unfocusUpdateTab(myTab);
                k2SetElementFocusState(versionTab, true);
            });

            myTab.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                focusUpdateTab(myTab);
                triggerCheck(e);
            });

            // Clean up versionTab in case it had corrupted inner children from previous attempts
            var verText = versionTab.querySelector('yt-formatted-string');
            if (verText && verText.textContent !== '앱 버전') {
                verText.textContent = '앱 버전';
            }

            // Insert right above the versionTab
            versionTab.parentElement.insertBefore(myTab, versionTab);
            console.log('[ZeroAd] Successfully injected native-styled update tab right above versionTab!');

            // Observe parent mutations so it never disappears on scroll / idom re-render
            var listParent = versionTab.parentElement;
            if (!listParent._k2ObserverAttached && window.MutationObserver) {
                listParent._k2ObserverAttached = true;
                var observer = new MutationObserver(function() {
                    k2InjectSettingsUpdateCard();
                });
                observer.observe(listParent, { childList: true });
            }
        } catch (e) {
            console.warn('[ZeroAd] Error injecting settings update card:', e);
        }
    }

    setInterval(k2InjectSettingsUpdateCard, 500);
    // Patches ONLY the Feedback panel (the one showing youtube.com/tv/feedback):
    // URL text -> github pulls URL, QR artwork -> pulls QR. Help Center and all
    // other panels untouched.
    function k2PatchFeedbackPanel() {
        try {
            // The feedback URL lives in a plain DIV (not yt-formatted-string):
            // scan visible setting-action panels for the marker text instead.
            var panels = document.querySelectorAll('ytlr-setting-action-renderer');
            for (var i = 0; i < panels.length; i++) {
                var p = panels[i];
                if (p._k2FbPatched) continue;
                var r = null;
                try { r = p.getBoundingClientRect(); } catch (e3) {}
                if (!r || r.width <= 0 || r.height <= 0) continue;
                var t = '';
                try { t = p.textContent || ''; } catch (e4) {}
                if (t.indexOf('youtube.com/tv/feedback') === -1) continue;
                k2ReplaceTextIn(p, 'youtube.com/tv/feedback', K2_GITHUB_PULLS_URL_TEXT);
                p._k2FbPatched = true;
                if (!window._k2FbLogged) {
                    window._k2FbLogged = true;
                    console.log('[ZeroAd] Feedback URL replaced with GitHub pulls URL.');
                }
                // QR thumbs in scope (the feedback panel currently shows an
                // illustration instead of a QR; kept future-proof).
                var thumbs = p.querySelectorAll ? p.querySelectorAll('ytlr-thumbnail-details') : [];
                for (var j = 0; j < thumbs.length; j++) {
                    var current = '';
                    try { current = thumbs[j].style.backgroundImage || ''; } catch (e1) {}
                    if (!current) {
                        try {
                            var cs = window.getComputedStyle(thumbs[j]);
                            if (cs) current = cs.backgroundImage || '';
                        } catch (e2) {}
                    }
                    if (current && current.indexOf('data:image') !== -1 &&
                        current.indexOf(K2_GITHUB_PULLS_QR_DATA_URL) === -1) {
                        thumbs[j].style.setProperty('background-image', 'url("' + K2_GITHUB_PULLS_QR_DATA_URL + '")', 'important');
                    }
                }
            }
        } catch (e) {
            console.warn('[ZeroAd] Error patching feedback panel:', e);
        }
    }

    // Near-instant DOM fallback: patch help/feedback panels the moment they are
    // inserted (microtask, pre-paint) instead of waiting for the 1s interval.
    // Gated on element insertions + 300ms throttle to stay cheap during playback.
    try {
        if (window.MutationObserver) {
            var _k2PanelPatchAt = 0;
            var _k2ObsRoot = document.documentElement || document;
            var _k2PanelObserver = new MutationObserver(function(muts) {
                try {
                    var now = Date.now();
                    if (now - _k2PanelPatchAt < 300) return;
                    for (var i = 0; i < muts.length; i++) {
                        var an = muts[i].addedNodes;
                        for (var j = 0; j < an.length; j++) {
                            if (an[j] && an[j].nodeType === 1) {
                                _k2PanelPatchAt = now;
                                k2PatchHelpCenterPanel();
                                k2PatchFeedbackPanel();
                                return;
                            }
                        }
                    }
                } catch (e) {}
            });
            _k2PanelObserver.observe(_k2ObsRoot, { childList: true, subtree: true });
        }
    } catch (e) {}

    setInterval(k2PatchHelpCenterPanel, 1000);
    setInterval(k2PatchFeedbackPanel, 1000);

    // =========================================================================
    // 14. Playback Speed Unlock (Up to 4.0x), OSD Badge & Remote Hotkeys Bridge
    // =========================================================================
    var K2_SPEED_RATES = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.5, 4.0];
    window._k2CurrentSpeed = 1.0;

    try {
        var savedRateStr = localStorage.getItem('yt-player-playback-rate');
        if (savedRateStr) {
            var parsed = JSON.parse(savedRateStr);
            var rVal = Number(parsed && (parsed.data || parsed));
            if (!isNaN(rVal) && rVal >= 0.25 && rVal <= 4.0) {
                window._k2CurrentSpeed = rVal;
            }
        }
    } catch (eSpeedInit) {}

    function showSpeedOsd(rate) {
        try {
            var parent = document.fullscreenElement || document.body;
            if (!parent) return;

            var badge = document.getElementById('k2-speed-badge');
            if (!badge) {
                badge = document.createElement('div');
                badge.id = 'k2-speed-badge';
                badge.style.cssText = [
                    'position: fixed',
                    'top: 32px',
                    'right: 32px',
                    'background: rgba(18, 18, 18, 0.92)',
                    'color: #00e5ff',
                    'border: 1.5px solid rgba(0, 229, 255, 0.8)',
                    'border-radius: 8px',
                    'padding: 6px 14px',
                    'font-size: 16px',
                    'font-weight: 700',
                    'font-family: Roboto, sans-serif',
                    'letter-spacing: 0.5px',
                    'box-shadow: 0 4px 16px rgba(0,0,0,0.85)',
                    'z-index: 2147483647',
                    'display: flex',
                    'align-items: center',
                    'gap: 8px',
                    'transition: opacity 0.25s ease, transform 0.25s ease',
                    'pointer-events: none',
                    'opacity: 0',
                    'transform: translateY(-8px) scale(0.96)'
                ].join(';');
            }

            // Ensure attached to top-most container
            if (badge.parentElement !== parent) {
                parent.appendChild(badge);
            }

            while (badge.firstChild) {
                badge.removeChild(badge.firstChild);
            }

            var icon = document.createElement('span');
            icon.textContent = '⚡';
            icon.style.fontSize = '18px';

            var label = (rate === 1.0) ? '1.0x (일반)' : (rate + 'x 속도');
            var text = document.createElement('span');
            text.textContent = label;

            badge.appendChild(icon);
            badge.appendChild(text);

            badge.style.opacity = '1';
            badge.style.transform = 'translateY(0) scale(1)';

            if (badge._timer) clearTimeout(badge._timer);
            badge._timer = setTimeout(function() {
                badge.style.opacity = '0';
                badge.style.transform = 'translateY(-8px) scale(0.96)';
            }, 1600);
        } catch (eOsd) {
            console.warn('[ZeroAd] OSD error:', eOsd);
        }
    }
    window.showSpeedOsd = showSpeedOsd;

    function k2KickVideoPlay(v) {
        if (!v) return;
        try {
            if (v.paused) {
                var p = v.play();
                if (p && typeof p.catch === 'function') p.catch(function() {});
            }
        } catch (e) {}
    }

    function k2ProtectAgainstStall(v) {
        if (!v) return;
        window._k2SpeedChanging = true;
        k2KickVideoPlay(v);
        setTimeout(function() { k2KickVideoPlay(v); }, 50);
        setTimeout(function() { k2KickVideoPlay(v); }, 150);
        setTimeout(function() { k2KickVideoPlay(v); }, 350);
        setTimeout(function() { k2KickVideoPlay(v); }, 700);
        setTimeout(function() { window._k2SpeedChanging = false; }, 1200);
    }

    window._k2InternalRateChange = false;

    window.k2SetPlaybackRate = function(rate) {
        try {
            var r = Number(rate);
            if (isNaN(r) || r < 0.25 || r > 4.0) return;
            window._k2CurrentSpeed = r;
            window._k2InternalRateChange = true;

            var vids = document.querySelectorAll('video');
            for (var i = 0; i < vids.length; i++) {
                try {
                    vids[i].playbackRate = r;
                    k2ProtectAgainstStall(vids[i]);
                } catch (eV) {}
            }

            var player = document.getElementById('movie_player') || document.querySelector('.html5-video-player');
            if (player) {
                if (typeof player.setPlaybackRate === 'function') {
                    try { player.setPlaybackRate(r); } catch (eP) {}
                }
            }

            try {
                localStorage.setItem('yt-player-playback-rate', JSON.stringify({
                    data: String(r),
                    expiration: Date.now() + 86400000 * 30
                }));
            } catch (eStore) {}

            showSpeedOsd(r);
            setTimeout(function() { window._k2InternalRateChange = false; }, 300);
        } catch (eSetRate) {
            window._k2InternalRateChange = false;
            console.warn('[ZeroAd] Error setting playback rate:', eSetRate);
        }
    };

    window.k2AdjustPlaybackRate = function(delta) {
        try {
            var cur = window._k2CurrentSpeed || 1.0;
            var curIdx = 3; // default 1.0
            var minDiff = 999;
            for (var i = 0; i < K2_SPEED_RATES.length; i++) {
                var diff = Math.abs(K2_SPEED_RATES[i] - cur);
                if (diff < minDiff) {
                    minDiff = diff;
                    curIdx = i;
                }
            }
            var nextIdx = curIdx + delta;
            if (nextIdx < 0) nextIdx = 0;
            if (nextIdx >= K2_SPEED_RATES.length) nextIdx = K2_SPEED_RATES.length - 1;
            window.k2SetPlaybackRate(K2_SPEED_RATES[nextIdx]);
        } catch (eAdj) {}
    };

    function k2HookPlayerRateMethods() {
        try {
            var player = document.getElementById('movie_player') || document.querySelector('.html5-video-player');
            if (player && !player._k2RateHooked) {
                player._k2RateHooked = true;
                player.getAvailablePlaybackRates = function() {
                    return K2_SPEED_RATES;
                };

                var origSetRate = player.setPlaybackRate;
                if (typeof origSetRate === 'function') {
                    player.setPlaybackRate = function(rate) {
                        var r = Number(rate);
                        if (!isNaN(r) && r > 0) {
                            if (!window._k2InternalRateChange) {
                                window._k2CurrentSpeed = r;
                                var v = document.querySelector('video');
                                if (v) {
                                    v.playbackRate = r;
                                    k2ProtectAgainstStall(v);
                                }
                                try {
                                    localStorage.setItem('yt-player-playback-rate', JSON.stringify({
                                        data: String(r),
                                        expiration: Date.now() + 86400000 * 30
                                    }));
                                } catch (eLs) {}
                                showSpeedOsd(r);
                            }
                        }
                        return origSetRate.apply(this, arguments);
                    };
                }
            }
        } catch (eHookPl) {}
    }

    window.k2OnSpeedChange = function(rate) {
        try {
            var r = Number(rate);
            if (!isNaN(r) && r > 0) {
                if (!window._k2InternalRateChange) {
                    window._k2CurrentSpeed = r;
                    var v = document.querySelector('video');
                    if (v) {
                        if (Math.abs(v.playbackRate - r) > 0.01) {
                            try { v.playbackRate = r; } catch (eV) {}
                        }
                        k2ProtectAgainstStall(v);
                    }
                    try {
                        localStorage.setItem('yt-player-playback-rate', JSON.stringify({
                            data: String(r),
                            expiration: Date.now() + 86400000 * 30
                        }));
                    } catch (eLs) {}
                    showSpeedOsd(r);
                }
            }
        } catch (eSpeed) {}
    };

    function k2EnsureSpeedOnPlaying() {
        try {
            var vids = document.querySelectorAll('video');
            for (var i = 0; i < vids.length; i++) {
                var v = vids[i];
                if (!v._k2SpeedHooked) {
                    v._k2SpeedHooked = true;
                    v.addEventListener('ratechange', function() {
                        var r = Number(this.playbackRate);
                        if (!isNaN(r) && r > 0) {
                            if (!window._k2InternalRateChange && Math.abs((window._k2CurrentSpeed || 1.0) - r) > 0.01) {
                                window._k2CurrentSpeed = r;
                                try {
                                    localStorage.setItem('yt-player-playback-rate', JSON.stringify({
                                        data: String(r),
                                        expiration: Date.now() + 86400000 * 30
                                    }));
                                } catch (eLs) {}
                                k2ProtectAgainstStall(this);
                                showSpeedOsd(r);
                            }
                        }
                    });
                    v.addEventListener('playing', function() {
                        if (window._k2CurrentSpeed && window._k2CurrentSpeed !== 1.0) {
                            if (Math.abs(this.playbackRate - window._k2CurrentSpeed) > 0.01) {
                                this.playbackRate = window._k2CurrentSpeed;
                            }
                        }
                    });
                    v.addEventListener('pause', function() {
                        if (window._k2SpeedChanging) {
                            k2KickVideoPlay(this);
                        }
                    });
                    v.addEventListener('waiting', function() {
                        if (window._k2SpeedChanging) {
                            k2KickVideoPlay(this);
                        }
                    });
                }
            }
            k2HookPlayerRateMethods();
        } catch (ePl) {}
    }

    function k2ExpandLiveSpeedMenu() {
        try {
            var panels = document.querySelectorAll('ytlr-overlay-panel-item-list-renderer');
            for (var pi = 0; pi < panels.length; pi++) {
                var p = panels[pi];
                if (p.__instance && p.__instance.props && p.__instance.props.data && p.__instance.props.data.items) {
                    k2ExpandSpeedItemsInArray(p.__instance.props.data.items);
                }
            }
        } catch (e) {}
    }

    setInterval(k2ExpandLiveSpeedMenu, 300);
    setInterval(k2EnsureSpeedOnPlaying, 1000);

    console.log("[ZeroAd] Ultra-Clean Zero-Ad Engine v8 fully engaged.");
})();
