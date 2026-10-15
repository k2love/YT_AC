# YouTube TV 클린룸 복제 앱 (Phase 1 결과 보고서)

## 1. 개요
- **목적**: 독점 바이너리(`libchrobalt.so`) 없이 순정 YouTube for Android TV(v7.28.300)의 UI/UX와 추천 알고리즘을 100% 동일하게 재현하는 클린룸(Clean-room) 앱의 1단계 구축 및 빌드 검증.
- **결과**: `BUILD SUCCESSFUL` (디버그 APK 생성 완료: `app-debug.apk`, 6.25 MB).

---

## 2. 주요 구현 내용

### 2.1 호스트 셸 및 하드웨어 가속 WebView (`TVWebView.kt`)
- **렌더링 파이프라인**: Android System WebView (하드웨어 가속 Blink/Chromium 코어).
- **User-Agent 위장**:
  ```text
  Mozilla/5.0 (ChromiumStylePlatform; Linux; Android 12; Chromecast) AppleWebKit/537.36 (KHTML, like Gecko) Cobalt/24.lts.5.1034102-gold (unlike Gecko) Starboard/16, Chrome/114.0.5735.196 Safari/537.36
  ```
- **WebSettings 최적화**: WebGL 2.0, DOM Storage, MSE, EME, 하드웨어 비디오 디코딩 전면 활성화.

### 2.2 Starboard / Cobalt `window.h5vcc` 시스템 폴리필 (`assets/h5vcc_polyfill.js`)
- 웹앱 로드 극초기(`onPageStarted`)에 DOM에 주입되어 순정 환경을 완벽 에뮬레이션:
  - `window.h5vcc.system`: `buildFingerprint`, `certificationScope: "sagit"`, `hardwareType: 1` (TV), `deviceYear: 2024`, `chipsetModelNumber`.
  - `window.h5vcc.storage`: 네이티브 영구 스토리지 플러시/초기화 인터페이스.
  - `window.h5vcc.platformService`: `has(name)`, `open(name, callback)`, `send(data)`, `close()`.
  - `window._onPlatformServiceReceive`: 네이티브에서 웹으로의 비동기 메시지 수신 함수.

### 2.3 12개 `CobaltService` 라우터 및 인증 동기화 (`PlatformServiceRouter.kt`)
- **`com.google.youtube.tv.syncauthcredential`** (`SyncAuthCredentialService.kt`):
  - 기동 시 유효한 저장 토큰이 있으면 `ReportAuthCredential` 자동 주입.
  - 웹 화면에서 로그인 시 `SyncAuthCredential` 메시지를 가로채어 `accessToken`, `expiry`, `ownerAccountEmail`, `activeVisitorData`, `dataSyncId`를 영구 저장.
- **`com.google.youtube.tv.recommendations`** (`RecommendationsService.kt`):
  - TV 런처 채널 및 셸프(`CONTINUE_WATCHING`, `SHORTS`) 갱신 처리.
- **`com.google.youtube.tv.networkmonitor`** (`NetworkMonitorService.kt`):
  - 실시간 대역폭 측정값 제공.
- **기타 9개 서비스**: 안전한 폴백 스텁 라우팅으로 크래시 차단.

### 2.4 풀스크린 및 리모컨 D-Pad 처리 (`MainActivity.kt`)
- `launch=menu` / `launch=remote` 자동 분기.
- Android TV 뒤로가기(Back) 및 D-Pad 키보드 이벤트 무지연 전달.

---

## 3. 빌드 및 산출물 정보
- **빌드 도구**: Gradle 8.13, AGP 8.5.2, Kotlin 1.9.24, Android SDK 34
- **결과**: `BUILD SUCCESSFUL in 51s`
- **산출물 위치**:
  `YouTubeTVClone/app/build/outputs/apk/debug/app-debug.apk` (약 6.25 MB)
