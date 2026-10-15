import os

polyfill_clean = '''(function() {
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
                if (lower.indexOf('vp9') !== -1 ||
                    lower.indexOf('vp09') !== -1 ||
                    lower.indexOf('av01') !== -1 ||
                    lower.indexOf('avc1') !== -1) {
                    return true;
                }
                return origIsTypeSupported(mimeType);
            };
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
            '[class*="scrim"] {',
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
        ].join('\\n');
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

    console.log("[ZeroAd] Ultra-Clean Zero-Ad Engine v8 fully engaged.");
})();
'''

target_path = os.path.join('YouTubeTVClone', 'app', 'src', 'main', 'assets', 'h5vcc_polyfill.js')
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(polyfill_clean.strip() + '\n')

print(f"Successfully generated clean {target_path} (size: {len(polyfill_clean)} bytes)")
