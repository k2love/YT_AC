// LG webOS Smart TV Remote Key Handler for YouTube TV AC
(function() {
    console.log("[webOSKeys] Initializing webOS Remote Controller binding...");

    // Intercept hardware Back key (461) on webOS
    window.addEventListener('keydown', function(event) {
        if (event.keyCode === 461) {
            console.log("[webOSKeys] webOS Hardware Back button pressed.");
            // 1. Dispatch Escape for YouTube Leanback UI back navigation
            var backEvent = new KeyboardEvent('keydown', {
                key: 'Escape',
                code: 'Escape',
                keyCode: 27,
                which: 27,
                bubbles: true,
                cancelable: true
            });
            document.dispatchEvent(backEvent);

            // 2. Prevent default webOS browser history pop if handled
            event.preventDefault();

            // 3. Close application if at root
            if (window.history.length <= 1) {
                if (window.webOS && window.webOS.platformBack) {
                    window.webOS.platformBack();
                } else if (window.close) {
                    window.close();
                }
            }
        }
    }, true);

    // Support webOS mouse/magic remote cursor hide/show on TV
    document.addEventListener('cursorStateChange', function(event) {
        console.log("[webOSKeys] Cursor visibility changed:", event.detail.visibility);
    });
})();
