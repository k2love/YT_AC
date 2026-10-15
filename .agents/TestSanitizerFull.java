import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class TestSanitizerFull {
    public static void main(String[] args) {
        try {
            String js = new String(Files.readAllBytes(Paths.get("YouTubeTVClone/app/src/main/assets/h5vcc_polyfill.js")), "UTF-8");
            String logoB64 = new String(Files.readAllBytes(Paths.get("YouTubeTVClone/app/src/main/assets/transparent_logo_b64.txt")), "UTF-8").trim();
            
            // Read a cached html or download one
            byte[] htmlBytes;
            if (Files.exists(Paths.get(".agents/cached_tv.html"))) {
                htmlBytes = Files.readAllBytes(Paths.get(".agents/cached_tv.html"));
            } else {
                System.out.println("No cached_tv.html, using mock youtube tv html");
                htmlBytes = ("<!DOCTYPE html><html><head><style>#loader {height: 100%; left: 0; position: absolute; top: 0; width: 100%; z-index: 0; background-position: center center; background-repeat: no-repeat; background-color: #282828;background-size: 60%;background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAB8AAAAG8CAMAAACWrk+4AAAAgVBMVEUoKC);}</style></head><body><script>var ytInitialData = {\"test\": 123}; var ytInitialPlayerResponse = {\"adPlacements\": []};</script></body></html>").getBytes("UTF-8");
            }
            String rawHtml = new String(htmlBytes, "UTF-8");
            
            System.out.println("Raw HTML length: " + rawHtml.length());
            
            String processed = rawHtml;
            
            // Step 3: oad replacement
            processed = processed.replaceAll("(oad|ovd|oaad|oavd)=\\d+", "no_ad=1");
            
            // Step 4: #loader CSS replacement
            if (!logoB64.isEmpty()) {
                String transparentLoaderCss = "#loader { height: 100%; left: 0; position: absolute; top: 0; width: 100%; z-index: 0; background-position: center center; background-repeat: no-repeat; background-color: transparent !important; background-size: 22% !important; background-image: url(\"" + logoB64 + "\") !important; }";
                System.out.println("Replacing #loader block with length: " + transparentLoaderCss.length());
                processed = processed.replaceAll("#loader\\s*\\{[^}]+\\}", Matcher.quoteReplacement(transparentLoaderCss));
            }
            
            // Step 5: inject inline script
            String splashLogoRule = "#loader, .splash-screen-loader { background-image: url(\"" + logoB64 + "\") !important; background-size: 22% !important; background-repeat: no-repeat !important; background-position: center !important; background-color: transparent !important; } ";
            String splashFixCss = "<style id=\"zero-ad-master-style\">html, body, #app-background { background: #000000 !important; background-color: #000000 !important; } #container { background: transparent !important; background-color: transparent !important; } " + splashLogoRule + ".ytp-gradient-bottom, .ytp-gradient-top, .ytp-chrome-bottom, .ytp-chrome-top, .ytp-chrome-controls, .ytp-title, .ytp-title-text, .ytp-title-channel, .ytp-tv-controls, .ytp-bottom-control-flexbox, .ytp-overlay, .player-controls, .player-controls-container, .ytlr-player-overlay, .ytp-pause-overlay, .ytp-player-content, [class*=\"gradient\"], [class*=\"scrim\"] { background: transparent !important; background-color: transparent !important; background-image: none !important; box-shadow: none !important; border: none !important; } .ytp-title-text, .ytp-title-channel, .ytp-time-display, .ytp-chapter-title-content { text-shadow: 0 1px 4px rgba(0,0,0,0.9), 0 0 2px rgba(0,0,0,0.9) !important; }</style>\n";
            String scriptTag = splashFixCss + "<script type=\"text/javascript\">\n" + js + "\n</script>\n";
            
            if (Pattern.compile("(?i)<head>").matcher(processed).find()) {
                processed = processed.replaceFirst("(?i)<head>", "<head>\n" + Matcher.quoteReplacement(scriptTag));
            }
            
            System.out.println("SUCCESS! Output HTML length: " + processed.length());
        } catch (Throwable t) {
            System.out.println("EXCEPTION: " + t.getClass().getName() + ": " + t.getMessage());
            t.printStackTrace(System.out);
        }
    }
}
