import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.nio.file.Files;
import java.nio.file.Paths;

public class TestRegex {
    public static void main(String[] args) {
        try {
            String js = new String(Files.readAllBytes(Paths.get("YouTubeTVClone/app/src/main/assets/h5vcc_polyfill.js")), "UTF-8");
            String html = "<html><head><title>Test</title></head><body>#loader { background: red; }</body></html>";
            
            System.out.println("Testing replaceFirst with js length: " + js.length());
            String scriptTag = "<script>" + js + "</script>";
            
            // This is what NativeAdSanitizer does:
            String processed = html.replaceFirst("(?i)<head>", "<head>\n" + scriptTag);
            System.out.println("Success! processed len: " + processed.length());
        } catch (Throwable t) {
            System.out.println("CAUGHT EXCEPTION: " + t.getClass().getName() + ": " + t.getMessage());
            t.printStackTrace(System.out);
        }
    }
}
