package com.k2.youtubetv.webview

import android.content.Context
import android.graphics.Bitmap
import android.util.Log
import android.webkit.CookieManager
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import okhttp3.Cache
import okhttp3.Headers
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import java.io.ByteArrayInputStream
import java.io.File
import java.util.concurrent.TimeUnit

class TVWebViewClient(private val context: Context) : WebViewClient() {

    companion object {
        private const val TAG = "TVWebViewClient"

        // Bump whenever patch logic changes: patched JS/CSS are cached on disk
        // keyed by URL, so without a version in the key, updated patches would
        // never take effect until the 24h cache entry expires.
        private const val PATCH_VERSION = 5

        // CSS gradient functions neutralized to kill Kabuki scrim overlays.
        // Order matters: longest names first so "-webkit-linear-gradient" is not
        // partially matched as "linear-gradient".
        private val GRADIENT_FUNCTIONS = arrayOf(
            "-webkit-linear-gradient",
            "-webkit-radial-gradient",
            "-webkit-gradient",
            "linear-gradient",
            "radial-gradient"
        )

        // Pure ad-network trackers, midrolls, and ad break triggers
        private val AD_URL_PATTERNS = arrayOf(
            "doubleclick.net",
            "googleads.g.doubleclick.net",
            "pubads.g.doubleclick.net",
            "pagead2.googlesyndication.com",
            "securepubads.g.doubleclick.net",
            "youtube.com/pagead/",
            "youtube.com/api/stats/ads",
            "youtube.com/get_midroll_info",
            "youtube.com/youtubei/v1/player/ad_break",
            "youtube.com/youtubei/v1/att/",
            "youtube.com/ptracking",
            "/get_midroll_info",
            "/player/ad_break",
            "/api/stats/ads",
            "/pagead/paralleladrequest"
        )
    }

    private var polyfillScript: String = ""
    private val patchedCacheDir = File(context.cacheDir, "patched_web_cache").apply { mkdirs() }

    private val httpClient: OkHttpClient = OkHttpClient.Builder()
        .cache(Cache(File(context.cacheDir, "tv_okhttp_cache"), 50L * 1024 * 1024))
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .followRedirects(true)
        .followSslRedirects(true)
        .build()

    private fun getCachedPatchedResponse(url: String, mimeType: String): WebResourceResponse? {
        val cleanUrl = url.substringBefore("#")
        val cacheKey = "v" + PATCH_VERSION + "_" + cleanUrl.hashCode().toString() + "_" + mimeType.replace("/", "_") + ".bin"
        val file = File(patchedCacheDir, cacheKey)
        if (file.exists() && file.length() > 0) {
            val age = System.currentTimeMillis() - file.lastModified()
            if (age < 24 * 3600 * 1000L) { // 24 hours
                return try {
                    val bytes = file.readBytes()
                    WebResourceResponse(
                        mimeType,
                        "utf-8",
                        200,
                        "OK",
                        emptyMap(),
                        ByteArrayInputStream(bytes)
                    )
                } catch (e: Exception) {
                    null
                }
            }
        }
        return null
    }

    private fun savePatchedResponseToCache(url: String, mimeType: String, bytes: ByteArray) {
        try {
            val cleanUrl = url.substringBefore("#")
            val cacheKey = "v" + PATCH_VERSION + "_" + cleanUrl.hashCode().toString() + "_" + mimeType.replace("/", "_") + ".bin"
            val file = File(patchedCacheDir, cacheKey)
            file.writeBytes(bytes)
        } catch (e: Exception) {
            Log.w(TAG, "Failed to write patched response to cache: ${e.message}")
        }
    }

    init {
        try {
            polyfillScript = context.assets.open("h5vcc_polyfill.js")
                .bufferedReader()
                .use { it.readText() }

            val logoB64 = context.assets.open("transparent_logo_b64.txt")
                .bufferedReader()
                .use { it.readText().trim() }
            NativeAdSanitizer.initLogo(logoB64)
            Log.d(TAG, "Successfully initialized transparent logo (len ${logoB64.length})")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to load assets in TVWebViewClient", e)
        }
    }

    override fun shouldInterceptRequest(view: WebView?, request: WebResourceRequest?): WebResourceResponse? {
        val url = request?.url?.toString() ?: return null

        // 1. Drop ad tracking beacons, midrolls, and ad break triggers
        if (isAdTrackerUrl(url)) {
            Log.d(TAG, "[Native-AdBlock] Blocked ad tracker / ad break: $url")
            return createEmpty204Response()
        }

        // 2. Drop pure video ad stream chunks (ONLY when adformat= or ad_type= exists)
        if (isPureVideoAdStream(url)) {
            Log.d(TAG, "[Native-AdBlock] Blocked pure video ad stream: $url")
            return createEmpty204Response()
        }

        // 3. Intercept and sanitize main HTML (https://www.youtube.com/tv*)
        if (isMainHtmlRequest(request, url)) {
            Log.d(TAG, "[Native-AdBlock] Intercepting & sanitizing YouTube TV main HTML: $url")
            val sanitizedResponse = fetchAndSanitizeHtml(url, request)
            if (sanitizedResponse != null) {
                return sanitizedResponse
            }
        }

        // 4. Intercept & patch player engine (tv-player-ias.js or its renamed bundles)
        if (isPlayerJsRequest(url)) {
            Log.d(TAG, "[Native-AdBlock] Intercepting & patching player JS: $url")
            val patchedResponse = fetchAndPatchJs(url, request, fullSurgical = true)
            if (patchedResponse != null) {
                return patchedResponse
            }
        }

        // 4b. Generic ad/quality patches for every other first-party app bundle.
        // Quality-cap logic may live outside the player file after YouTube
        // refactors; the generic patches are no-ops where patterns are absent.
        if (isAppJsRequest(url)) {
            val patchedResponse = fetchAndPatchJs(url, request, fullSurgical = false)
            if (patchedResponse != null) {
                return patchedResponse
            }
        }

        // 5. Intercept & neutralize gradient scrims in EVERY first-party stylesheet
        // (kabuki.css URL patterns change with YouTube updates; limiting to one
        // filename lets scrims through unpatched, rendering as opaque black boxes).
        if (isCssRequest(url)) {
            Log.d(TAG, "[Native-Transparent] Intercepting & neutralizing stylesheet: $url")
            val transparentCssResponse = fetchAndNeutralizeCss(url, request)
            if (transparentCssResponse != null) {
                return transparentCssResponse
            }
        }

        return super.shouldInterceptRequest(view, request)
    }

    private fun isPureVideoAdStream(url: String): Boolean {
        if (url.contains("googlevideo.com/videoplayback")) {
            if (url.contains("adformat=") ||
                url.contains("ad_type=") ||
                url.contains("&oad=") ||
                url.contains("&ad_cpn=")
            ) {
                return true
            }
        }
        return false
    }

    private fun isPlayerJsRequest(url: String): Boolean {
        if (!url.contains(".js")) return false
        if (url.contains("tv-player") || url.contains("player_ias") ||
            url.contains("player-plasma") || url.contains("cobalt-player")
        ) return true
        // Fallback: YouTube renames obfuscated player bundles frequently.
        // Any first-party JS with "player" in the name gets the ad/quality patches
        // (patches are no-op string replaces when patterns are absent).
        return url.contains("youtu") && url.contains("player")
    }

    private fun isAppJsRequest(url: String): Boolean {
        if (!url.contains(".js")) return false
        if (isPlayerJsRequest(url)) return false // handled with full surgical patches
        if (url.contains("doubleclick") || url.contains("pagead") ||
            url.contains("googlesyndication") || url.contains("adsbygoogle")
        ) return false
        if (url.contains("cast_sender") || url.contains("cast_framework")) return false
        return url.contains("youtu") || url.contains("gstatic")
    }

    private fun fetchAndPatchJs(url: String, request: WebResourceRequest?, fullSurgical: Boolean): WebResourceResponse? {
        val cached = getCachedPatchedResponse(url, "application/javascript")
        if (cached != null) {
            Log.d(TAG, "[Fast-Cache] Returning cached patched JS: $url")
            return cached
        }

        return try {
            val requestBuilder = Request.Builder().url(url)
            request?.requestHeaders?.forEach { (k, v) ->
                if (!k.equals("Accept-Encoding", ignoreCase = true)) {
                    requestBuilder.addHeader(k, v)
                }
            }
            // Forward WebView cookies: some player bundles vary by session/consent.
            val cookie = CookieManager.getInstance().getCookie(url)
            if (!cookie.isNullOrEmpty()) {
                requestBuilder.header("Cookie", cookie)
            }
            val response = httpClient.newCall(requestBuilder.build()).execute()
            if (!response.isSuccessful) return null
            syncCookies(url, response.headers)

            var js = response.body?.string() ?: return null

            // Ad patches safe in ANY app bundle (pure literals / ad-check shapes,
            // no-ops where patterns are absent):
            // 1. Force ad-checking functions to always return false
            js = js.replace(Regex("""if\s*\(![a-zA-Z0-9_$]+\|\|![a-zA-Z0-9_$]+\.adPlacements&&![a-zA-Z0-9_$]+\.adSlots\)return!1;"""), "return!1;")
            js = js.replace("if(!N||!N.adPlacements&&!N.adSlots)return!1;", "return!1;")
            // 2. Neutralize playerAds
            js = js.replace(Regex("""var\s+[a-zA-Z0-9_$]+=this\.playerResponse\.playerAds;"""), "var n=null;")
            js = js.replace("var n=this.playerResponse.playerAds;", "var n=null;")
            // 3. Disable ad-showing classes
            js = js.replace("\"ad-showing\"", "\"no-ad-showing\"")
            js = js.replace("\"ad-interrupting\"", "\"no-ad-interrupting\"")

            // 4. Kabuki router patches to prevent overshooting / redirecting to Account Selector:
            // 4a. Block Cast Protection account selector in router.Fg()
            val fgCastProtectionRegex = Regex("""if\s*\(_\.txa\(this\.history\.Ca\(\)\)\s*&&\s*_\.As\(_\.H\.get\(_\.Bs\)\)\)""")
            if (fgCastProtectionRegex.containsMatchIn(js)) {
                js = js.replace(fgCastProtectionRegex, "if(!1)")
                Log.d(TAG, "[Router-Fix] Neutralized Cast Protection account selector in router Fg()")
            }

            // 4b. Expose command dispatcher to window for clean home navigation
            val kkRegex = Regex("""_\.kk=function\(\)\{return _\.Zx\.instance\};""")
            if (kkRegex.containsMatchIn(js)) {
                js = js.replace(kkRegex, "_.kk=function(){window._k2CommandDispatcher=_.Zx.instance;return _.Zx.instance};")
                Log.d(TAG, "[Router-Fix] Bound window._k2CommandDispatcher via _.kk")
            }

            // 4c. Intercept resolveCommand to prevent ANY unintended account selector command on back navigation
            val resolveCmdRegex = Regex("""\.prototype\.resolveCommand=function\(([a-zA-Z0-9_$]+),([a-zA-Z0-9_$]+)\)\{return _\.ay\(this,\1,\2\)\.handled\};""")
            if (resolveCmdRegex.containsMatchIn(js)) {
                js = js.replace(resolveCmdRegex, """.prototype.resolveCommand=function($1,$2){
                    if($1&&($1.requestAccountSelectorCommand||$1.restartToAccountSelectorCommand||$1.startAccountSelectorCommand)){
                        var tr=($1.requestAccountSelectorCommand&&$1.requestAccountSelectorCommand.identityActionContext&&$1.requestAccountSelectorCommand.identityActionContext.eventTrigger)||"";
                        if(tr==="ACCOUNT_EVENT_TRIGGER_CAST_PROTECTION"||window._k2InBackNavigation||window._k2HasLoadedHome){
                            return this.resolveCommand({browseEndpoint:{browseId:"default"}},$2);
                        }
                    }
                    return _.ay(this,$1,$2).handled;
                };""".trimIndent())
                Log.d(TAG, "[Router-Fix] Installed resolveCommand account selector guard")
            }

            if (fullSurgical) {
                // Player bundle only from here down: (0,720)/(0,1080) tuples or
                // getAdBreakUrl identifiers in unrelated bundles may mean seconds,
                // pixels, or other wiring — never touch them outside the player.
                // 4. Disable getAdBreakUrl to prevent post-start ad injections
                js = js.replace("getAdBreakUrl", "disabledAdBreakUrl")

                // Generic fallback: any explicit numeric 720p/1080p resolution-cap
                // constructors (constructor-name agnostic: catches renames the
                // surgical patches miss).
                val numCap720 = Regex("""new\s+([A-Za-z_$][\w$]*)\(0,720,!1""")
                val numCap1080 = Regex("""new\s+([A-Za-z_$][\w$]*)\(0,1080,!1""")
                val n720 = numCap720.findAll(js).count()
                val n1080 = numCap1080.findAll(js).count()
                js = js.replace(numCap720, "new \$1(0,4320,!1")
                js = js.replace(numCap1080, "new \$1(0,4320,!1")
                if (n720 + n1080 > 0) Log.d(TAG, "[4K-Unlock] Generic numeric-cap fallback raised ${n720 + n1080} clamps (720p x$n720, 1080p x$n1080) to 4320 [player JS]")

                // Force Unlock 4K (2160p) & 8K (4320p) by disabling viewport, chipset, and default quality caps
                // Each surgical patch is verified: if YouTube renames the obfuscated symbols,
                // the count stays 0 and logcat warns instead of silently falling back to 720p.
                // Patch B3 (viewport resolution cap -> pass through 8K 4320p max)
                val b3Regex = Regex("""CF\.prototype\.B3=function\(N\)\{.+?return new DA\(0,L,!1,"r"\)\};""", RegexOption.DOT_MATCHES_ALL)
                val b3Count = b3Regex.findAll(js).count()
                js = js.replace(b3Regex, "CF.prototype.B3=function(N){return new DA(0,4320,!1,\"r\");};")
                Log.d(TAG, "[4K-Unlock] B3 viewport-cap patch applied x$b3Count")
                if (b3Count == 0) Log.w(TAG, "[4K-Unlock] B3 pattern NOT found — YouTube may have renamed symbols, 720p cap may persist!")

                // Patch k2 (html5_chipset_soft_cap & html5_max_vertical_resolution -> pass through 8K 4320p max)
                val k2Regex = Regex("""function k2\(N,L\)\{.+?return new DA\(0,\s*v,!1,"o"\)\}""", RegexOption.DOT_MATCHES_ALL)
                val k2Count = k2Regex.findAll(js).count()
                js = js.replace(k2Regex, "function k2(N,L){return new DA(0,4320,!1,\"o\");}")
                Log.d(TAG, "[4K-Unlock] k2 chipset-cap patch applied x$k2Count")
                if (k2Count == 0) Log.w(TAG, "[4K-Unlock] k2 pattern NOT found — YouTube may have renamed symbols, 720p cap may persist!")

                // Patch w$n (html5_default_quality_cap -> default to 4320p)
                val wCapRegex = Regex("""var\s+g=ar\(N\.G\.experiments,"html5_default_quality_cap"\);""")
                val wCapCount = wCapRegex.findAll(js).count()
                js = js.replace(wCapRegex, "var g=4320;")
                Log.d(TAG, "[4K-Unlock] default-quality-cap patch applied x$wCapCount")
                if (wCapCount == 0) Log.w(TAG, "[4K-Unlock] default-quality-cap pattern NOT found — check obfuscation drift!")

                // Patch w$n live/HFR/random caps (each flag string occurs exactly once
                // in tv-player-ias.js). Renaming the flag makes ar() return undefined
                // so the Math.min clamp is skipped:
                // - html5_live_quality_cap: clamps EVERY live playback (e.g. to 480p)
                // - html5_hfr_quality_cap: clamps whenever any variant is fps>32,
                //   i.e. all 720p60/1080p60 live renditions
                // - html5_random_playback_cap: nonce dice-roll cap on any playback
                val extraCaps = mapOf(
                    "html5_live_quality_cap" to "live",
                    "html5_hfr_quality_cap" to "hfr",
                    "html5_random_playback_cap" to "random"
                )
                for ((flag, label) in extraCaps) {
                    val count = js.split("\"$flag\"").size - 1
                    js = js.replace("\"$flag\"", "\"${flag}_k2off\"")
                    Log.d(TAG, "[4K-Unlock] $label-quality-cap flag disabled x$count")
                    if (count == 0) Log.w(TAG, "[4K-Unlock] $flag NOT found — check obfuscation drift!")
                }

                // Patch gv() HFR gate: formats with fps>32 are blocked with "capHfr"
                // unless v.Fx or HH(FRAMERATE) passes. The HH sanity probe pairs a
                // realistic value (framerate=30) with an impossible one
                // (framerate=9999) and our MSE layer must answer both truthfully,
                // which flips the verdict on clients whose WebView ignores the
                // extended params. Neutralize the gate itself (single occurrence):
                // 60fps HD then flows into the (already uncapped) ladder and ABR.
                val hfrGate = "if(!v.Fx&&!HH(v,j6.FRAMERATE))return\"capHfr\";"
                val hfrCount = js.split(hfrGate).size - 1
                js = js.replace(hfrGate, "if(!1)return\"capHfr\";")
                Log.d(TAG, "[4K-Unlock] HFR capHfr gate disabled x$hfrCount")
                if (hfrCount == 0) Log.w(TAG, "[4K-Unlock] capHfr gate NOT found — check obfuscation drift!")

                // Patch playback speed upper limit (unlock 2.0x limit to 4.0x)
                // 1) Default max playback rate: this.nM=2; -> this.nM=4;
                val nmCount = js.split("this.nM=2;").size - 1
                js = js.replace("this.nM=2;", "this.nM=4;")
                Log.d(TAG, "[Speed-Unlock] default max rate nM=2 patched to 4 x$nmCount")

                // 2) Server granularVariableSpeedConfig clamp: this.nM=gm/100 -> this.nM=Math.max(4,gm/100)
                val gmCount = js.split("this.nM=gm/100").size - 1
                js = js.replace("this.nM=gm/100", "this.nM=Math.max(4,gm/100)")
                Log.d(TAG, "[Speed-Unlock] granular server rate clamp patched to max(4,gm/100) x$gmCount")

                // 3) Hook player setPlaybackRate to always persist rate & notify bridge
                val origSetRate = "v.getPlaybackRate()!==N&&(v.setPlaybackRate(N),L&&fa(\"yt-player-playback-rate\",N),this.Sl.DX(\"onPlaybackRateChange\",N))"
                val patchedSetRate = "v.getPlaybackRate()!==N&&(v.setPlaybackRate(N),fa(\"yt-player-playback-rate\",N),this.Sl.DX(\"onPlaybackRateChange\",N),window.k2OnSpeedChange&&window.k2OnSpeedChange(N))"
                val srCount = js.split(origSetRate).size - 1
                js = js.replace(origSetRate, patchedSetRate)
                Log.d(TAG, "[Speed-Unlock] player setPlaybackRate persistence & bridge hooked x$srCount")

                // 4) Patch new video startup rate restoration (iIZ)
                val origInitRate = "Number(ZD(\"yt-player-playback-rate\"))||1"
                val patchedInitRate = "(window._k2CurrentSpeed||(typeof ZD===\"function\"?(function(){var x=ZD(\"yt-player-playback-rate\");return Number(x&&x.data||x);})():1)||1)"
                val initCount = js.split(origInitRate).size - 1
                js = js.replace(origInitRate, patchedInitRate)
                Log.d(TAG, "[Speed-Unlock] player iIZ init rate patched x$initCount")

                // 5) Patch NF playback rate clamp to allow rates up to 4.0x
                val origNfClamp = "F=F[F[v[l^3812]]-1];a<=G||(a>=F?G=F:"
                val patchedNfClamp = "F=Math.max(4,F[F[v[l^3812]]-1]);a<=G||(a>=F?G=F:"
                val nfCount = js.split(origNfClamp).size - 1
                js = js.replace(origNfClamp, patchedNfClamp)
                Log.d(TAG, "[Speed-Unlock] NF playback rate clamp patched to 4.0x x$nfCount")

                // 6) Patch available playback rates filter to include up to 4.0x
                val origFilter = "var L=N.jW,g=N.Cj;return oBf.filter(function(a){return a>=L&&a<=g})"
                val patchedFilter = "var L=N.jW,g=Math.max(4,N.Cj||2);return oBf.filter(function(a){return a>=L&&a<=g})"
                val filterCount = js.split(origFilter).size - 1
                js = js.replace(origFilter, patchedFilter)
                Log.d(TAG, "[Speed-Unlock] oBf available rates filter patched to 4.0x x$filterCount")

                // 7) Patch oBf array to include 2.25 and 2.75
                val origObf = "oBf=s1f.concat([2.5,3,3.5,4])"
                val patchedObf = "oBf=s1f.concat([2.25,2.5,2.75,3,3.5,4])"
                val obfCount = js.split(origObf).size - 1
                js = js.replace(origObf, patchedObf)
                Log.d(TAG, "[Speed-Unlock] oBf rate ladder expanded with 2.25 & 2.75 x$obfCount")

                // Fallbacks for older player variants
                val origAu1Clamp = "v=v[v.length-1];L<=N?L=N:L>=v?L=v:"
                val patchedAu1Clamp = "v=Math.max(4,v[v.length-1]);L<=N?L=N:L>=v?L=v:"
                js = js.replace(origAu1Clamp, patchedAu1Clamp)

                val origWsFilter = "return WsS.filter(function(g){return g>=L&&g<=v})"
                val patchedWsFilter = "return WsS.filter(function(g){return g>=L&&g<=Math.max(4,v||2)})"
                js = js.replace(origWsFilter, patchedWsFilter)
            }

            val bytes = js.toByteArray(Charsets.UTF_8)
            savePatchedResponseToCache(url, "application/javascript", bytes)
            WebResourceResponse(
                "application/javascript",
                "utf-8",
                200,
                "OK",
                emptyMap(),
                ByteArrayInputStream(bytes)
            )
        } catch (e: Exception) {
            Log.e(TAG, "Error fetching & patching player JS: ${e.message}", e)
            null
        }
    }

    private fun isCssRequest(url: String): Boolean {
        // First-party stylesheets only, so third-party embeds are never slowed down.
        if (!(url.contains("youtube") || url.contains("gstatic") || url.contains("googlevideo"))) return false
        val path = url.substringBefore("?").lowercase()
        return path.endsWith(".css") || url.contains("/_/kabuki/_/ss/")
    }

    private fun fetchAndNeutralizeCss(url: String, request: WebResourceRequest?): WebResourceResponse? {
        val cached = getCachedPatchedResponse(url, "text/css")
        if (cached != null) {
            Log.d(TAG, "[Fast-Cache] Returning cached neutralized CSS: $url")
            return cached
        }

        return try {
            val requestBuilder = Request.Builder().url(url)
            request?.requestHeaders?.forEach { (k, v) ->
                if (!k.equals("Accept-Encoding", ignoreCase = true)) {
                    requestBuilder.addHeader(k, v)
                }
            }
            val cookie = CookieManager.getInstance().getCookie(url)
            if (!cookie.isNullOrEmpty()) {
                requestBuilder.header("Cookie", cookie)
            }
            val response = httpClient.newCall(requestBuilder.build()).execute()
            if (!response.isSuccessful) return null
            syncCookies(url, response.headers)

            var css = response.body?.string() ?: return null

            // Neutralize all linear & radial gradient scrims.
            // NOTE: balanced-paren scanner (not "[^)]+" regex) because gradient args
            // contain nested parens like rgba(0,0,0,.5) that naive regexes leave behind
            // as "none, rgba(...))" remnants, breaking the CSS rule.
            var gradientKills = 0
            for (fn in GRADIENT_FUNCTIONS) {
                val (next, count) = replaceCssFunction(css, fn, "none")
                css = next
                gradientKills += count
            }
            Log.d(TAG, "[Native-Transparent] Neutralized $gradientKills gradient scrims in stylesheet")

            // Append master transparent rules for Kabuki classes + YouTube TV player
            // chrome (control bar, title card, overlays). Dialog cards, buttons and
            // progress elements are intentionally NOT listed: nuking their
            // backgrounds would destroy readability and focus indication.
            val appendRules = "\n.Vdm04:before, .Vdm04:after, .leUgff, .YHA8m, .dwgyh, .wTHb2c, .r4Pyib, .bel0Db, .q7Ygpb, [class*=\"Vdm04\"] { background: transparent !important; background-image: none !important; box-shadow: none !important; border: none !important; }\n" +
                "ytlr-player-controls, ytlr-control-bar, ytlr-title-card-renderer, [class*=\"control-bar\"], [class*=\"ControlBar\"], [class*=\"player-control\"], [class*=\"PlayerControl\"], [class*=\"title-card\"], [class*=\"TitleCard\"], [class*=\"video-title\"], [class*=\"VideoTitle\"], [class*=\"player-overlay\"], [class*=\"PlayerOverlay\"] { background: transparent !important; background-color: transparent !important; background-image: none !important; box-shadow: none !important; border: none !important; }\n"
            css += appendRules

            val bytes = css.toByteArray(Charsets.UTF_8)
            savePatchedResponseToCache(url, "text/css", bytes)
            WebResourceResponse(
                "text/css",
                "utf-8",
                200,
                "OK",
                emptyMap(),
                ByteArrayInputStream(bytes)
            )
        } catch (e: Exception) {
            Log.e(TAG, "Error neutralizing stylesheet: ${e.message}", e)
            null
        }
    }

    /**
     * Replaces every `fnName(...)` call with [replacement], skipping balanced
     * parentheses (handles nested rgba()/color-mix() args). Returns the new
     * string plus the number of replacements made.
     */
    private fun replaceCssFunction(css: String, fnName: String, replacement: String): Pair<String, Int> {
        val sb = StringBuilder(css.length)
        var i = 0
        var count = 0
        while (i < css.length) {
            val idx = css.indexOf(fnName, i, ignoreCase = true)
            if (idx == -1) {
                sb.append(css, i, css.length)
                break
            }
            var j = idx + fnName.length
            while (j < css.length && css[j].isWhitespace()) j++
            if (j >= css.length || css[j] != '(') {
                sb.append(css, i, j.coerceAtMost(css.length))
                i = j
                continue
            }
            sb.append(css, i, idx)
            sb.append(replacement)
            count++
            // Skip the balanced parenthesized argument list.
            var depth = 0
            var k = j
            var inStr = false
            var strCh = '\u0000'
            while (k < css.length) {
                val c = css[k]
                if (inStr) {
                    if (c == strCh) inStr = false
                } else {
                    if (c == '"' || c == '\'') {
                        inStr = true
                        strCh = c
                    } else if (c == '(') {
                        depth++
                    } else if (c == ')') {
                        depth--
                        if (depth == 0) {
                            k++
                            break
                        }
                    }
                }
                k++
            }
            i = k
        }
        return Pair(sb.toString(), count)
    }

    private fun isAdTrackerUrl(url: String): Boolean {
        for (pattern in AD_URL_PATTERNS) {
            if (url.contains(pattern)) {
                return true
            }
        }
        return false
    }

    private fun isMainHtmlRequest(request: WebResourceRequest?, url: String): Boolean {
        if (request == null) return false
        val method = request.method
        if (!method.equals("GET", ignoreCase = true)) return false

        // Check if it's the main YouTube TV entry point
        if (url.startsWith("https://www.youtube.com/tv") || url.startsWith("http://www.youtube.com/tv")) {
            val accept = request.requestHeaders?.get("Accept") ?: ""
            if (request.isForMainFrame || accept.contains("text/html") || !url.contains(".")) {
                return true
            }
        }
        return false
    }

    private fun fetchAndSanitizeHtml(url: String, request: WebResourceRequest): WebResourceResponse? {
        return try {
            val requestBuilder = Request.Builder().url(url)

            // Forward headers from WebView
            request.requestHeaders?.forEach { (k, v) ->
                if (!k.equals("Accept-Encoding", ignoreCase = true)) {
                    requestBuilder.addHeader(k, v)
                }
            }

            // Forward cookies
            val cookie = CookieManager.getInstance().getCookie(url)
            if (!cookie.isNullOrEmpty()) {
                requestBuilder.header("Cookie", cookie)
            }

            val response: Response = httpClient.newCall(requestBuilder.build()).execute()
            if (!response.isSuccessful) {
                return null
            }

            // Sync received cookies back to WebView
            syncCookies(url, response.headers)

            val rawHtml = response.body?.string() ?: return null
            val sanitizedHtml = NativeAdSanitizer.sanitizeHtml(rawHtml, polyfillScript)
            val bytes = sanitizedHtml.toByteArray(Charsets.UTF_8)

            val contentType = response.header("Content-Type", "text/html; charset=utf-8") ?: "text/html; charset=utf-8"
            val mimeType = if (contentType.contains(";")) contentType.substringBefore(";").trim() else "text/html"
            val encoding = "utf-8"

            val responseHeaders = mutableMapOf<String, String>()
            for (i in 0 until response.headers.size) {
                val name = response.headers.name(i)
                val value = response.headers.value(i)
                if (!name.equals("Content-Encoding", ignoreCase = true) &&
                    !name.equals("Content-Length", ignoreCase = true)
                ) {
                    responseHeaders[name] = value
                }
            }

            WebResourceResponse(
                mimeType,
                encoding,
                response.code,
                response.message.ifEmpty { "OK" },
                responseHeaders,
                ByteArrayInputStream(bytes)
            )
        } catch (e: Exception) {
            Log.e(TAG, "Error fetching & sanitizing HTML: ${e.message}", e)
            null
        }
    }

    private fun syncCookies(url: String, headers: Headers) {
        val cookieManager = CookieManager.getInstance()
        val setCookies = headers.values("Set-Cookie")
        for (sc in setCookies) {
            cookieManager.setCookie(url, sc)
        }
        cookieManager.flush()
    }

    private fun createEmpty204Response(): WebResourceResponse {
        return WebResourceResponse(
            "text/plain",
            "utf-8",
            204,
            "No Content",
            emptyMap(),
            ByteArrayInputStream(ByteArray(0))
        )
    }

    override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
        super.onPageStarted(view, url, favicon)
        Log.d(TAG, "Page started: $url")
        injectPolyfill(view)
    }

    override fun onPageFinished(view: WebView?, url: String?) {
        super.onPageFinished(view, url)
        Log.d(TAG, "Page finished: $url")
        injectPolyfill(view)
    }

    override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
        val url = request?.url?.toString() ?: return false
        Log.d(TAG, "shouldOverrideUrlLoading: $url")
        if (url.contains("youtube.com")) {
            return false
        }
        return false
    }

    private fun injectPolyfill(view: WebView?) {
        if (polyfillScript.isNotEmpty() && view != null) {
            view.evaluateJavascript(polyfillScript) { result ->
                Log.d(TAG, "Polyfill injection evaluated: $result")
            }
        }
    }
}
