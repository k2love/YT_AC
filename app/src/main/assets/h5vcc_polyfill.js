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

        // Safely unlock VP9 & AV1 4K formats in MediaSource without breaking EME/DRM
        if (window.MediaSource && typeof window.MediaSource.isTypeSupported === 'function') {
            var origIsTypeSupported = window.MediaSource.isTypeSupported.bind(window.MediaSource);
            window.MediaSource.isTypeSupported = function(mimeType) {
                if (!mimeType) return false;
                var lower = mimeType.toLowerCase();
                // Video: VP8/VP9/AV1/H.264 (proven decodable via WebView MSE).
                // NOTE: HEVC (hev1/hvc1) is deliberately NOT affirmed: claiming an
                // undecodable codec makes ABR pick it, fail, and cascade down to
                // 720p. Audio: affirm common codecs so audio filtering never
                // drops a ladder entry.
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
            for (var i = obj.length - 1; i >= 0; i--) {
                var item = obj[i];
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
                }
                sanitizeAdsDirectly(item);
            }
        } else {
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
    var QUALITY_ORDER = ['hd2880', 'hd2160', 'hd1440', 'hd1080', 'hd720', 'large', 'medium', 'small', 'tiny'];

    function k2QualityRank(q) {
        var i = QUALITY_ORDER.indexOf(q);
        return i === -1 ? 999 : i;
    }

    function k2MissingHigh(player, have) {
        var need2160 = false, need1440 = false;
        try {
            var cur = (player && typeof player.getPlaybackQuality === 'function') ? player.getPlaybackQuality() : '';
            if (cur === 'hd2880' || cur === 'hd2160') { need2160 = true; need1440 = true; }
            else if (cur === 'hd1440') { need1440 = true; }
        } catch (e) {}
        try {
            var v = document.querySelector('video');
            if (v && v.videoWidth >= 3700) { need2160 = true; need1440 = true; }
            else if (v && v.videoWidth >= 2500) { need1440 = true; }
        } catch (e2) {}
        try {
            // Session peak per video: if this video already played at UHD (even
            // if ABR currently dipped), the formats provably exist.
            var mr = (typeof window._k2MaxRank === 'number') ? window._k2MaxRank : 999;
            if (mr <= 1) { need2160 = true; need1440 = true; }
            else if (mr <= 2) { need1440 = true; }
        } catch (e3) {}
        var out = [];
        if (need2160 && !have['hd2160']) out.push('hd2160');
        if (need1440 && !have['hd1440']) out.push('hd1440');
        return out;
    }

    function k2EnsureQualityWrap() {
        try {
            var player = document.getElementById('movie_player') || document.querySelector('.html5-video-player');
            if (!player || player._k2QWrapped) return;
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
                    if (!extra.length) return list;
                    var out = list.slice();
                    for (var k = 0; k < extra.length; k++) out.push(extra[k]);
                    var auto = out.indexOf('auto') !== -1;
                    out = out.filter(function(q) { return q !== 'auto'; });
                    out.sort(function(a, b) { return k2QualityRank(a) - k2QualityRank(b); });
                    if (auto) out.unshift('auto');
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
                    // Shape-agnostic data clone: duplicate the 1080p entry and
                    // rewrite its quality-ish fields to 2160p/1440p. The app then
                    // renders/focuses/selects them with its own correct layout —
                    // no DOM surgery, no broken rows.
                    try {
                        var have = {}, tpl = null;
                        for (var i = 0; i < arr.length; i++) {
                            var it = arr[i];
                            if (!it || typeof it !== 'object') continue;
                            var sig = '';
                            try { sig = JSON.stringify(it); } catch (e3) { continue; }
                            if (/\b2160\b/.test(sig)) have['hd2160'] = true;
                            if (/\b1440\b/.test(sig)) have['hd1440'] = true;
                            if (!tpl && /\b1080\b/.test(sig)) tpl = it;
                        }
                        var extra = k2MissingHigh(player, have);
                        if (extra.length && tpl) {
                            for (var k = 0; k < extra.length; k++) {
                                var num = extra[k].replace('hd', '');
                                var clone = null;
                                try { clone = JSON.parse(JSON.stringify(tpl)); } catch (e4) {}
                                if (!clone) continue;
                                for (var f in clone) {
                                    if (typeof clone[f] === 'string' && /\b1080\b/.test(clone[f]) &&
                                        /qual|label|level|name|id|height/i.test(f)) {
                                        clone[f] = clone[f].replace(/1080/g, num);
                                    } else if (typeof clone[f] === 'number' && clone[f] === 1080 &&
                                               /qual|label|level|name|id|height/i.test(f)) {
                                        clone[f] = parseInt(num, 10);
                                    }
                                }
                                arr.push(clone);
                            }
                        }
                    } catch (e5) {}
                    return arr;
                };
                wrappedAny = true;
            }

            if (wrappedAny) {
                player._k2QWrapped = true;
                console.log('[ZeroAd] quality menu API wrapped for UHD exposure.');
                try {
                    if (typeof _origLevels === 'function') {
                        var _raw = _origLevels() || [];
                        console.log('[ZeroAd-Telemetry] rawLevels=[' + _raw.join(',') + ']');
                    }
                } catch (e9) {}
                try {
                    if (typeof _origData === 'function') {
                        var _rd = _origData() || [];
                        var _k0 = (_rd.length && _rd[0] && typeof _rd[0] === 'object') ? Object.keys(_rd[0]).join(',') : String(typeof _rd[0]);
                        console.log('[ZeroAd-Telemetry] rawDataShape=[' + _k0 + '] len=' + _rd.length);
                    }
                } catch (e10) {}
            }
        } catch (e) {}
    }

    // =========================================================================
    // 5d. Browse-URL memory: Neutralized to prevent overshooting to account picker.
    // YouTube TV manages its view stack internally (Kabuki router); forcing
    // location.replace() reloads the app back into ?launch=menu (account picker).
    // =========================================================================
    window._k2LastBrowse = null;

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
    // 7. YouTube TV Settings Screen Update Widget Injector
    // Injects an "App Info & Update" card into the settings menu
    // =========================================================================
    function k2InjectSettingsUpdateCard() {
        try {
            var isSettings = window.location.hash.indexOf('settings') !== -1 ||
                             window.location.href.indexOf('/settings') !== -1 ||
                             !!document.querySelector('[role="menu"][aria-label*="설정"], [role="menu"][aria-label*="Settings"], ytlr-settings-category-renderer');
            if (!isSettings) return;

            if (document.getElementById('yt-ac-settings-update-banner')) return;

            // Find an optimal settings container
            var container = document.querySelector('ytlr-settings-category-renderer, [role="menu"], #settings-content, .settings-container, #container');
            if (!container) return;

            var card = document.createElement('div');
            card.id = 'yt-ac-settings-update-banner';
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'button');
            card.setAttribute('aria-label', 'YT_TV_AC 앱 정보 및 업데이트 확인');
            card.style.cssText = 'margin: 16px 24px; padding: 18px 24px; background: rgba(255,255,255,0.08); border: 2px solid rgba(255,255,255,0.2); border-radius: 12px; cursor: pointer; outline: none; transition: all 0.2s;';

            card.innerHTML = '<div style="font-size: 20px; font-weight: bold; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">🚀 YT_TV_AC 설정 및 최신 업데이트 확인</div>' +
                             '<div style="font-size: 14px; color: #AAAAAA; margin-top: 6px;">무제한 Zero-Ad · 4K/8K 언락 · 현재 버전: v1.0.0 (리모컨 선택 시 업데이트 확인)</div>';

            card.addEventListener('focus', function() {
                card.style.background = 'rgba(255,255,255,0.2)';
                card.style.borderColor = '#3EA6FF';
                card.style.transform = 'scale(1.02)';
            });
            card.addEventListener('blur', function() {
                card.style.background = 'rgba(255,255,255,0.08)';
                card.style.borderColor = 'rgba(255,255,255,0.2)';
                card.style.transform = 'scale(1)';
            });

            function triggerCheck() {
                if (window.YT_TV_APP && typeof window.YT_TV_APP.checkAppUpdate === 'function') {
                    window.YT_TV_APP.checkAppUpdate();
                }
            }

            card.addEventListener('click', triggerCheck);
            card.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.keyCode === 13) {
                    triggerCheck();
                }
            });

            container.insertBefore(card, container.firstChild);
            console.log('[ZeroAd] Settings update card injected successfully.');
        } catch (e) {}
    }

    setInterval(k2InjectSettingsUpdateCard, 1500);

    console.log("[ZeroAd] Ultra-Clean Zero-Ad Engine v8 fully engaged.");
})();
