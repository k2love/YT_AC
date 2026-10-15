package com.k2.youtubetv.webview

import android.util.Log
import org.json.JSONArray
import org.json.JSONObject

object NativeAdSanitizer {

    private const val TAG = "NativeAdSanitizer"
    private var transparentLogoB64: String = ""

    fun initLogo(b64: String) {
        transparentLogoB64 = b64
    }

    private val AD_KEYS_TO_REMOVE = setOf(
        "adslotrenderer",
        "infeedadrenderer",
        "mastheadadrenderer",
        "mastheadrenderer",
        "heroadrenderer",
        "promotedvideorenderer",
        "promotedsparkleswebrenderer",
        "statementbannerrenderer",
        "bannerpromorenderer",
        "adbreakservicerenderer",
        "playerads",
        "adbreakheartbeatparams",
        "interstitials",
        "adbreakrenderer",
        "instreamadbreakrenderers",
        "adunit",
        "adlayouts",
        "brandvideorenderer"
    )

    fun sanitizeJson(jsonString: String): String {
        val trimmed = jsonString.trim()
        if (trimmed.isEmpty()) return jsonString

        return try {
            if (trimmed.startsWith("{")) {
                val obj = JSONObject(trimmed)
                cleanJsonObject(obj)
                obj.toString()
            } else if (trimmed.startsWith("[")) {
                val arr = JSONArray(trimmed)
                cleanJsonArray(arr)
                arr.toString()
            } else {
                jsonString
            }
        } catch (e: Exception) {
            Log.w(TAG, "Error sanitizing JSON, returning original: ${e.message}")
            jsonString
        }
    }

    private fun cleanJsonObject(obj: JSONObject) {
        val keys = mutableListOf<String>()
        val it = obj.keys()
        while (it.hasNext()) {
            keys.add(it.next())
        }

        for (key in keys) {
            val lower = key.lowercase()

            // 1. YouTube Player API ad placements & slots -> Neutralize with empty array
            if (lower == "adplacements" || lower == "adslots") {
                obj.put(key, JSONArray())
                continue
            }

            // 1b. Raise server-driven quality caps (chipset / default / max-resolution
            // experiment flags) to 8K 4320p so the player ladder is never clipped.
            if (lower.contains("quality_cap") || lower.contains("max_vertical_resolution") ||
                lower.contains("chipset_soft_cap")
            ) {
                if (obj.opt(key) is Number) {
                    obj.put(key, 4320)
                    continue
                }
            }

            // 2. Pure ad objects -> Remove entirely
            if (AD_KEYS_TO_REMOVE.contains(lower)) {
                obj.remove(key)
                continue
            }

            val value = obj.opt(key) ?: continue
            when (value) {
                is JSONObject -> cleanJsonObject(value)
                is JSONArray -> cleanJsonArray(value)
            }
        }
    }

    private fun cleanJsonArray(arr: JSONArray) {
        for (i in arr.length() - 1 downTo 0) {
            val item = arr.opt(i) ?: continue
            if (item is JSONObject) {
                if (isAdWrapper(item)) {
                    arr.remove(i)
                } else {
                    cleanJsonObject(item)
                }
            } else if (item is JSONArray) {
                cleanJsonArray(item)
            }
        }
    }

    private fun isAdWrapper(obj: JSONObject): Boolean {
        val it = obj.keys()
        while (it.hasNext()) {
            val k = it.next().lowercase()
            if (AD_KEYS_TO_REMOVE.contains(k)) {
                return true
            }
        }
        return false
    }

    fun sanitizeHtml(html: String, inlineScript: String): String {
        var processed = html

        // 1. Sanitize ytInitialData using robust brace counting
        processed = extractAndSanitizeVariable(processed, "ytInitialData")

        // 2. Sanitize ytInitialPlayerResponse
        processed = extractAndSanitizeVariable(processed, "ytInitialPlayerResponse")

        // 3. Neutralize online ad prefetch parameters in initplayback (/initplayback?...oad=3200...)
        processed = processed.replace(Regex("""(oad|ovd|oaad|oavd)=\d+"""), "no_ad=1")

        // 4. Surgically replace original opaque #loader CSS block with pure transparent logo
        if (transparentLogoB64.isNotEmpty()) {
            val transparentLoaderCss = "#loader { height: 100%; left: 0; position: absolute; top: 0; width: 100%; z-index: 0; background-position: center center; background-repeat: no-repeat; background-color: transparent !important; background-size: 22% !important; background-image: url(\"$transparentLogoB64\") !important; }"
            processed = processed.replace(Regex("""#loader\s*\{[^}]+\}"""), java.util.regex.Matcher.quoteReplacement(transparentLoaderCss))
        }

        // 5. Inject inline polyfill & Zero-Ad script & splash size/transparency fix right after <head> or at top
        val splashFixCss = "<style id=\"zero-ad-master-style\">html, body, #app-background { background: #000000 !important; background-color: #000000 !important; } #container { background: transparent !important; background-color: transparent !important; } #loader, .splash-screen-loader { background-size: 22% !important; background-color: transparent !important; } .ytp-gradient-bottom, .ytp-gradient-top, .ytp-chrome-bottom, .ytp-chrome-top, .ytp-chrome-controls, .ytp-title, .ytp-title-text, .ytp-title-channel, .ytp-tv-controls, .ytp-bottom-control-flexbox, .ytp-overlay, .player-controls, .player-controls-container, .ytlr-player-overlay, .ytp-pause-overlay, .ytp-player-content, [class*=\"gradient\"], [class*=\"scrim\"], [class*=\"Vdm04\"], [class*=\"Vdm04\"]:before, [class*=\"Vdm04\"]:after, .leUgff, .YHA8m, .dwgyh, .wTHb2c, .r4Pyib, .bel0Db, .q7Ygpb, .XpH8cb, .QvTwo, .jYycK { background: transparent !important; background-color: transparent !important; background-image: none !important; box-shadow: none !important; border: none !important; } .ytp-title-text, .ytp-title-channel, .ytp-time-display, .ytp-chapter-title-content { text-shadow: 0 1px 4px rgba(0,0,0,0.9), 0 0 2px rgba(0,0,0,0.9) !important; }</style>\n"
        val scriptTag = "$splashFixCss<script type=\"text/javascript\">\n$inlineScript\n</script>\n"
        val quotedScriptTag = java.util.regex.Matcher.quoteReplacement(scriptTag)
        processed = if (processed.contains("<head>", ignoreCase = true)) {
            processed.replaceFirst("(?i)<head>".toRegex(), "<head>\n$quotedScriptTag")
        } else if (processed.contains("<html>", ignoreCase = true)) {
            processed.replaceFirst("(?i)<html>".toRegex(), "<html><head>\n$quotedScriptTag</head>")
        } else {
            scriptTag + processed
        }

        return processed
    }

    private fun extractAndSanitizeVariable(source: String, varName: String): String {
        val searchPatterns = arrayOf(
            "$varName = ",
            "$varName=",
            "\"$varName\"] = ",
            "\"$varName\"]="
        )

        for (pattern in searchPatterns) {
            val varIndex = source.indexOf(pattern)
            if (varIndex != -1) {
                val braceStart = source.indexOf('{', varIndex + pattern.length)
                if (braceStart != -1) {
                    val braceEnd = findMatchingBrace(source, braceStart)
                    if (braceEnd != -1) {
                        try {
                            val rawJson = source.substring(braceStart, braceEnd + 1)
                            val cleanedJson = sanitizeJson(rawJson)
                            Log.d(TAG, "Successfully extracted and sanitized $varName (len ${rawJson.length} -> ${cleanedJson.length})")
                            return source.substring(0, braceStart) + cleanedJson + source.substring(braceEnd + 1)
                        } catch (e: Exception) {
                            Log.w(TAG, "Failed to parse extracted JSON for $varName: ${e.message}")
                        }
                    }
                }
            }
        }
        return source
    }

    private fun findMatchingBrace(str: String, startIdx: Int): Int {
        var depth = 0
        var inString = false
        var isEscaped = false

        for (i in startIdx until str.length) {
            val c = str[i]

            if (isEscaped) {
                isEscaped = false
                continue
            }

            if (c == '\\') {
                isEscaped = true
                continue
            }

            if (c == '"') {
                inString = !inString
                continue
            }

            if (!inString) {
                if (c == '{') {
                    depth++
                } else if (c == '}') {
                    depth--
                    if (depth == 0) {
                        return i
                    }
                }
            }
        }
        return -1
    }
}
