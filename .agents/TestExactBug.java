import java.nio.file.Files;
import java.nio.file.Paths;

public class TestExactBug {
    public static void main(String[] args) {
        try {
            String js = new String(Files.readAllBytes(Paths.get("YouTubeTVClone/app/src/main/assets/h5vcc_polyfill.js")), "UTF-8");
            String html = "<html><head></head><body></body></html>";
            
            String scriptTag = "<script>" + js + "</script>";
            
            // EXACT Kotlin code:
            // processed.replaceFirst("(?i)<head>".toRegex(), "<head>\n$scriptTag")
            System.out.println("Calling replaceFirst WITHOUT quoteReplacement...");
            String result = html.replaceFirst("(?i)<head>", "<head>\n" + scriptTag);
            System.out.println("Result length: " + result.length());
        } catch (Throwable t) {
            System.out.println("BOOM! CRASH DETECTED:");
            t.printStackTrace(System.out);
        }
    }
}
