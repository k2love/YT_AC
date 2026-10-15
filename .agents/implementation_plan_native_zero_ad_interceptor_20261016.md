# YouTube TV 클린룸 v1.1: 네이티브 레벨 원천 광고 차단(Native Zero-Ad Interceptor) 계획서

## 1. 개요 및 사용자 피드백 분석
- **보고된 문제**: 
  1. 홈 화면 대문짝 스폰서(Masthead) 광고 잔존.
  2. 일반 영상 사이사이 인피드 스폰서 광고 잔존.
  3. 영상 클릭 시 강제/연장 광고가 패스되는 과정이 보이고, 오히려 강제/연장 광고가 계속 나오는 현상 발생.
- **원인 분석**:
  - YouTube TV 웹앱은 초기 홈 피드를 HTML 내부의 정적 `<script>window.ytInitialData = {...}</script>`로 수신하여 렌더링함.
  - `WebViewCompat.addDocumentStartJavaScript`는 기기 및 웹뷰 버전에 따라 실행이 누락되거나 지연될 수 있음.
  - `h5vcc_polyfill.js`의 `fetch`/`XHR` 후킹은 초기 HTML에 박힌 `ytInitialData`를 막지 못하며, 플레이어 API 응답이 후킹 전에 전달될 경우 인스트림 광고 엔진이 트리거됨.
  - JS 레벨의 `video.currentTime = video.duration` 방식은 유튜브 최신 플레이어의 다중 연속 광고(Ad 1 of 2, 2 of 2)에서 광고 스킵 실패 루프를 유발함.

## 2. 해결 전략: 네이티브 4중 원천 차단(Native MITM Sanitizer)
JavaScript 후킹에만 의존하지 않고, 안드로이드 네이티브의 `WebViewClient.shouldInterceptRequest`에서 트래픽을 가로채어 완벽한 무광고 데이터로 정제:

1. **초기 진입 HTML 정제 (`https://www.youtube.com/tv*`)**:
   - 네이티브에서 HTML을 받아 `<script>...ytInitialData = ...</script>` 추출.
   - `mastheadRenderer`, `adSlotRenderer`, `inFeedAdRenderer` 등 모든 스폰서 노드를 네이티브 JSON 파서로 삭제 후 재주입.
   - `<head>` 최상단에 Zero-Ad CSS 및 H5VCC 브릿지 스크립트를 인라인 직접 삽입.
2. **플레이어 API 가로채기 (`/youtubei/v1/player*`)**:
   - 네이티브 `OkHttpClient`로 요청 대리 수행.
   - 응답 JSON에서 `adPlacements`, `playerAds`, `adSlots`, `adBreakHeartbeatParams`, `interstitials` 완전 삭제.
   - 플레이어가 광고 없는 프리미엄 상태로 인식하여 즉시 본 영상 0초부터 재생.
3. **피드/검색/다음 영상 API 정제 (`/youtubei/v1/browse*`, `/youtubei/v1/next*`, `/youtubei/v1/search*`)**:
   - 모든 인피드 스폰서, 프로모션 카드 삭제 후 반환.
4. **광고 스트림 및 비콘 원천 드롭**:
   - `googlevideo.com/videoplayback` 중 `&adformat=` 또는 `&ctier=` 파라미터가 포함된 광고 스트림 즉시 204 No Content.
   - Google AdSense, DoubleClick, Ptracking 등 204 No Content.

## 3. 세부 구현 대상 파일
- `YouTubeTVClone/app/src/main/java/com/k2/youtubetv/webview/NativeAdSanitizer.kt` (신규: 네이티브 JSON 및 HTML 정제 엔진)
- `YouTubeTVClone/app/src/main/java/com/k2/youtubetv/webview/TVWebViewClient.kt` (개조: `shouldInterceptRequest`에서 MITM 처리 및 프록시 파이프라인 탑재)
- `YouTubeTVClone/app/src/main/assets/h5vcc_polyfill.js` (보강: CSS 선택자 전수 보강 및 DOM 감시 강화)

## 4. 검증 계획
1. 단위 테스트 / 스크립트 검증: YouTube InnerTube JSON 샘플 대상 정제기 동작 테스트.
2. `.\gradlew.bat assembleDebug` 빌드 무결성 확인.
3. 최종 APK 산출물 생성 및 릴리즈 준비.
