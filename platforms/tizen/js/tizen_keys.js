// Tizen Smart TV Remote Key Handler for YouTube TV AC
(function() {
    console.log("[TizenKeys] Initializing Tizen TV Remote Controller binding...");

    if (window.tizen && window.tizen.tvinputdevice) {
        var supportedKeys = [
            'MediaPlay',
            'MediaPause',
            'MediaPlayPause',
            'MediaStop',
            'MediaFastForward',
            'MediaRewind',
            'ColorF0Red',
            'ColorF1Green',
            'ColorF2Yellow',
            'ColorF3Blue',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
        ];

        supportedKeys.forEach(function(keyName) {
            try {
                tizen.tvinputdevice.registerKey(keyName);
            } catch (err) {
                // Ignore unsupported keys on specific Tizen versions
            }
        });
    }

    // Intercept hardware Back key (10009) on Tizen
    window.addEventListener('keydown', function(event) {
        if (event.keyCode === 10009) {
            console.log("[TizenKeys] Tizen Hardware Back button pressed.");
            // 1. Dispatch Escape or simulate Back for YouTube Leanback
            var backEvent = new KeyboardEvent('keydown', {
                key: 'Escape',
                code: 'Escape',
                keyCode: 27,
                which: 27,
                bubbles: true,
                cancelable: true
            });
            document.dispatchEvent(backEvent);

            // 2. If at root, ask Tizen application to exit
            if (window.history.length <= 1) {
                try {
                    tizen.application.getCurrentApplication().exit();
                } catch (e) {}
            }
        }
    }, true);
})();
