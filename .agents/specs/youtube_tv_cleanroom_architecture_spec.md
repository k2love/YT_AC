# YouTube for Android TV 클린룸 아키텍처 사양서 (Part 3: 100% 원본 복제 구현 설계)

본 문서는 YouTube for Android TV (v7.28.300)의 리버스 엔지니어링 결과를 바탕으로, 원본 앱의 독점 바이너리(`libchrobalt.so` 등)를 일체 사용하지 않고 클린룸(Clean-Room) 방식으로 100% 오리지널 UI/UX와 계정 맞춤 추천 알고리즘을 완벽 재현하기 위한 종합 아키텍처 및 구현 기술 명세서입니다.

---

## 1. SmartTube 대비 오리지널 앱 복제의 우위 분석

| 비교 항목 | SmartTube (서드파티) | 오리지널 YouTube TV 클린룸 복제 앱 |
| :--- | :--- | :--- |
| **UI/UX 엔진** | Android Leanback UI (XML/Compose)로 간이 재구성 | 오리지널 Kabuki WebGL/HTML5 웹앱 그대로 렌더링 |
| **시각적 완성도** | 폰트, 애니메이션, 포커스 전환, 사운드 등에서 이질감 발생 | 오리지널과 100% 동일한 픽셀 단위 UI 및 트랜지션 |
| **추천 알고리즘** | 모바일/익명 InnerTube API 크롤링으로 맞춤도 저하 | `activeVisitorData`, `dataSyncId`, `SyncAuthCredential` 연동으로 실제 유튜브 홈 화면 100% 동기화 |
| **재생 파이프라인** | 자체 ExoPlayer 패치 기반 | Chromium MSE/EME 하드웨어 가속 파이프라인 |
| **원격 제어(Cast)** | 서드파티 mDNS / DIAL 간이 수신 | `com.google.android.gms.cast.tv` 프로토콜 기반 순정 캐스트 연동 |

---

## 2. 클린룸 복제 아키텍처 설계 (System Architecture)

```
+-----------------------------------------------------------------------------+
|                  Original Web Frontend (Kabuki Runtime)                     |
|                   URL: https://www.youtube.com/tv?launch=menu                |
|       - 100% 오리지널 TV 레이아웃, 포커스 네비게이션, 맞춤 추천 피드       |
+-----------------------------------------------------------------------------+
                                      |
                      window.h5vcc Polyfill Bridge
                                      |
+-------------------------------------v---------------------------------------+
|              Android System WebView (Chromium Hardware Engine)              |
|       - Hardware Accelerated Video / WebGL / MSE / EME (Widevine)           |
|       - User-Agent & Client Hints Spoofing (Cobalt/Starboard UA)            |
+-----------------------------------------------------------------------------+
                                      | @JavascriptInterface
+-------------------------------------v---------------------------------------+
|                    Native Bridge Core (Kotlin / Android TV)                 |
|                                                                             |
|  [H5vccSystemModule]       [PlatformServiceManager]     [AuthSyncCoordinator]|
|  - ro.build.fingerprint    - 12개 CobaltService IPC      - AccountManager     |
|  - cert_scope (sagit)      - JSON 메시지 양방향 라우팅   - Token Refresh Task |
|                                                                             |
|  [ChannelRecommendation]   [RemoteButtonHandler]        [AudioVideoOptimizer]|
|  - Leanback Watch Next     - launch=remote / menu        - 4K VP9/AV1 60fps   |
+-----------------------------------------------------------------------------+
```

---

## 3. 핵심 모듈별 정밀 구현 사양

### 3.1 Web Engine & User-Agent 위장 사양
Google의 YouTube TV 서버(`https://www.youtube.com/tv`)는 일반 브라우저로 접속할 경우 지원되지 않는 브라우저 안내 페이지를 반환하거나 모바일 페이지로 리다이렉트합니다. 원본 Cobalt 런타임으로 인식시키기 위해 다음 사양을 적용합니다.

- **접속 URL**: `https://www.youtube.com/tv?launch=menu`
- **User-Agent 문자열 사양**:
  ```text
  Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36
  ```
- **WebView 설정 요구사항**:
  - `settings.javaScriptEnabled = true`
  - `settings.domStorageEnabled = true`
  - `settings.databaseEnabled = true`
  - `settings.mediaPlaybackRequiresUserGesture = false`
  - `settings.setSupportMultipleWindows(false)`
  - 하드웨어 가속 레이어 활성화: `setLayerType(View.LAYER_TYPE_HARDWARE, null)`

---

### 3.2 `window.h5vcc` JavaScript Polyfill 사양
웹앱이 로드되는 순간(`onPageStarted` 및 HTML 파싱 극초기) 다음 네이티브 모킹 객체를 DOM에 주입합니다.

```javascript
(function() {
    if (window.h5vcc) return;

    window.h5vcc = {
        system: {
            buildFingerprint: NativeBridge.getBuildFingerprint(),
            hardwareType: 1, // TV Device
            deviceYear: 2024,
            chipsetModelNumber: NativeBridge.getChipset(),
            areSystemNotificationCardsEnabled: false,
            certificationScope: "sagit"
        },
        storage: {
            clear: function() { NativeBridge.storageClear(); },
            flush: function() { NativeBridge.storageFlush(); }
        },
        settings: {
            // Cobalt TV 전용 설정 플래그
        },
        runtime: {
            initialDeepLink: ""
        },
        platformService: {
            has: function(serviceName) {
                return NativeBridge.hasPlatformService(serviceName);
            },
            open: function(serviceName, callback) {
                const serviceId = NativeBridge.openPlatformService(serviceName);
                window._platformServiceCallbacks = window._platformServiceCallbacks || {};
                window._platformServiceCallbacks[serviceId] = callback;

                return {
                    send: function(jsonString) {
                        NativeBridge.sendPlatformService(serviceId, jsonString);
                    },
                    close: function() {
                        NativeBridge.closePlatformService(serviceId);
                        delete window._platformServiceCallbacks[serviceId];
                    }
                };
            }
        }
    };

    // 네이티브에서 웹으로 메시지 전달 시 호출되는 수신 인터페이스
    window._onPlatformServiceReceive = function(serviceId, jsonString) {
        if (window._platformServiceCallbacks && window._platformServiceCallbacks[serviceId]) {
            window._platformServiceCallbacks[serviceId](jsonString);
        }
    };
})();
```

---

### 3.3 계정 인증 동기화 (`AuthSyncCoordinator`) 구현 사양

1. **기기 구글 계정 토큰 자동 추출**:
   - `AccountManager` 또는 `GoogleAuthUtil.getToken(context, account, "oauth2:https://www.googleapis.com/auth/youtube")`를 백그라운드 코루틴에서 실행.
2. **`SyncAuthCredential` 서비스 양방향 바인딩**:
   - 웹앱이 오픈하는 `com.google.youtube.tv.syncauthcredential` 서비스 ID를 캐싱.
   - 앱 기동 시 네이티브에서 웹으로 `ReportAuthCredential` 전송:
     ```json
     {
       "action": "ReportAuthCredential",
       "message": {
         "accessToken": "ya29...",
         "expiry": 1729050000000,
         "ownerAccountEmail": "user@gmail.com"
       }
     }
     ```
   - 사용자가 TV 화면 상에서 로그인/계정 전환을 실행할 때 발생하는 `SyncAuthCredential` 메시지를 네이티브 `EncryptedSharedPreferences`에 영구 보존.

---

### 3.4 Android TV 홈 화면 채널 및 추천 연동 사양
`com.google.youtube.tv.recommendations` 서비스로 웹앱이 보내오는 추천 데이터를 Android TV Leanback `TvContractCompat`에 삽입:
- `TvContractCompat.Channels`: "YouTube 맞춤 동영상", "YouTube Shorts" 채널 등록
- `TvContractCompat.PreviewPrograms`: 영상 제목, 썸네일 URL, 재생 지속 시간, 딥링크 URI(`https://www.youtube.com/tv?v=...`) 저장

---

## 4. 재구현 마일스톤 및 단계별 검증 기준

```
[Phase 1] 셸 컨테이너 및 UA/h5vcc 주입 -> 검증: 순정 https://www.youtube.com/tv 100% 렌더링
[Phase 2] 리모컨 D-Pad 포커스 및 미디어 재생 -> 검증: 4K 60fps VP9/AV1 영상 부드럽게 재생
[Phase 3] SyncAuthCredential 연동 -> 검증: 구글 계정 로그인 및 진짜 맞춤 추천 피드 로드
[Phase 4] Recommendations 채널 & Cast 연동 -> 검증: TV 런처 추천 등록 및 모바일 캐스트 수신
```
