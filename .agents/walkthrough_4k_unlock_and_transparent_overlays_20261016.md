# 워크스루: YouTube TV 4K(2160p) 해상도 언락, 완전 투명 로고/컨트롤 적용 및 사후 광고 박멸

## 1. 개요 및 해결 요약
본 작업에서는 사용자가 지적한 3가지 핵심 결함(4K 강제 다운그레이드, 로고/문자/컨트롤의 검정 불투명 배경, 영상 재생 후 1~2초 뒤 튀어나오는 강제 광고)을 리버스 엔지니어링을 통해 근본 원인을 파악하고 정밀하게 해결하였습니다.

---

## 2. 근본 원인 분석 및 해결 내역

### A. 2160p 이상의 영상이 720p로 강제 다운그레이드되던 원인 및 해결
- **진짜 원인**:
  1. Android TV의 디스플레이 프레임버퍼 밀도(MDPI 160 기준)로 인해 WebView JavaScript의 `window.screen.width`가 `1280`x`720`으로 보고되고 있었습니다.
  2. YouTube TV의 Adaptive Video Streaming 알고리즘은 화면 크기가 720p이면 대역폭 절약을 위해 1080p 및 4K(2160p) 스트림을 지원 대상에서 제외(Cap)합니다.
  3. 또한 기존 `h5vcc.system.buildFingerprint`가 1080p 전용 1세대 기기인 `eureka`로 설정되어 있었고, `MediaSource.isTypeSupported` 및 `navigator.mediaCapabilities`가 4K VP9/AV1 쿼리에 대해 보수적으로 응답하고 있었습니다.
- **해결 조치**:
  1. `window.screen.width = 3840`, `screen.height = 2160`, `screen.availWidth = 3840`, `screen.availHeight = 2160`, `devicePixelRatio = 2.0` 오버라이드.
  2. `MediaSource.isTypeSupported` 패치: `vp9`, `vp09`, `av01`, `avc1` 등 4K UHD 코덱 쿼리에 대해 무조건 `true` 반환.
  3. `navigator.mediaCapabilities.decodingInfo` 패치: 4K 60fps 비디오 디코딩 시 `supported: true, smooth: true, powerEfficient: true` 보장.
  4. H5VCC 시스템 핑거프린트를 **Chromecast with Google TV (4K)** 정식 모델인 `sabrina`(`google/sabrina/sabrina:12/STTE.231215.005/11324838:user/release-keys`)로 교체.

---

### B. 로고 및 문자, 컨트롤 뒤의 검정 배경 잔존 원인 및 해결
- **진짜 원인**:
  1. YouTube TV 웹페이지(`https://www.youtube.com/tv`)의 `#loader` CSS에 박혀있던 `data:image/png;base64,...` 이미지는 투명 PNG가 아니라, **배경이 `RGB(40, 40, 40)`으로 가득 차 있는 1984x444 크기의 불투명 인덱스 PNG**였습니다.
  2. 따라서 CSS에서 아무리 `background-color: transparent`를 주어도 이미지 파일 자체가 불투명했기 때문에 로고 뒤에 네모난 판이 보였던 것입니다.
  3. 또한 컨트롤 메뉴(`.ytp-chrome-bottom`, `.ytp-title`, `.player-controls`)의 CSS `linear-gradient`를 Android TV WebView의 GPU 컴포지터가 제대로 알파 블렌딩하지 못하고 검은 단색 상자로 렌더링하는 현상이 있었습니다.
- **해결 조치**:
  1. 불투명 회색 배경을 알파=0 완전 투명으로 변환한 순수 RGBA PNG Data URI(`.agents/transparent_logo_b64.txt`)를 `assets`에 배치.
  2. `NativeAdSanitizer.kt`에서 원본 HTML을 파싱할 때 `#loader` CSS 블록 자체를 서지컬하게 완전 투명 Data URI 및 순정 크기(`background-size: 22% !important`)로 교체.
  3. 모든 컨트롤 오버레이(`.ytp-gradient-bottom, .ytp-chrome-bottom, .ytp-title, .ytp-tv-controls, [class*="gradient"], [class*="scrim"]`)에 대해 `background: transparent !important; background-image: none !important; box-shadow: none !important; border: none !important;` 강제 적용.
  4. 텍스트 가독성을 위해 순정 느낌의 부드러운 `text-shadow: 0 1px 4px rgba(0,0,0,0.9)` 부여.

---

### C. 영상 재생 후 1~2초 뒤에 튀어나오던 강제 광고 원천 박멸
- **진짜 원인**:
  - YouTube 플레이어가 영상 재생 직후 비동기로 하트비트 세션(`adBreakHeartbeatParams`) 및 미드롤 정보(`/youtubei/v1/player/ad_break`, `/get_midroll_info`)를 호출하여 사후 광고를 삽입.
- **해결 조치**:
  1. `JSON.parse` 전역 몽키패치에서 파싱되는 모든 객체의 `adPlacements`, `adSlots`, `playerAds`, `adBreakHeartbeatParams`, `getAdBreakUrl`, `playbackTracking`을 즉각 삭제(`delete`).
  2. `TVWebViewClient`에서 미드롤 및 애드브레이크 요청을 즉시 `204 No Content`로 드롭.
  3. `instantAdKiller` 실행 주기를 **15ms**로 단축하고, 비디오 엘리먼트(`video`)에 광고 플래그가 붙는 즉시 음소거(`muted = true`) 및 재생 시간 스킵(`currentTime = duration`)으로 0초 만에 무력화.

---

## 3. 수정된 핵심 파일 및 변경 사항

1. **`YouTubeTVClone/app/src/main/assets/h5vcc_polyfill.js`**:
   - 4K Screen 규격, MediaSource 4K 코덱 언락, MediaCapabilities 패치 적용.
   - H5VCC 4K 정식 핑거프린트(`sabrina`) 적용.
   - 완전 투명 로고 Base64 Data URI 및 투명 오버레이 CSS 일괄 적용.
   - 15ms 주기 Zero-Tolerance Ad Killer 적용.
2. **`YouTubeTVClone/app/src/main/java/com/k2/youtubetv/webview/NativeAdSanitizer.kt`**:
   - `transparentLogoB64` 로드 및 초기화 메서드(`initLogo`) 추가.
   - HTML 원본의 불투명 `#loader` 규칙을 투명 Data URI로 직접 치환.
   - `<head>` 인라인 스타일에 컨트롤 투명화 및 텍스트 섀도우 주입.
3. **`YouTubeTVClone/app/src/main/java/com/k2/youtubetv/webview/TVWebViewClient.kt`**:
   - 앱 기동 시 `assets`의 `transparent_logo_b64.txt`를 읽어 `NativeAdSanitizer`에 바인딩.
4. **`YouTubeTVClone/app/src/main/assets/transparent_logo_b64.txt`**:
   - 알파=0 순수 투명 RGBA 변환 로고 Data URI 보관.

---

## 4. 빌드 및 무결성 검증 결과

- **Gradle 빌드 결과**:
  - 명령: `.\gradlew.bat assembleDebug`
  - 결과: **`BUILD SUCCESSFUL in 2s`** (38 actionable tasks)
- **APK 산출물**:
  - 파일 경로: `YouTubeTVClone/app/build/outputs/apk/debug/app-debug.apk`
  - 파일 크기: **`7,246,734 바이트 (약 7.25 MB)`**
- **인코딩 검증**:
  - `h5vcc_polyfill.js`, `NativeAdSanitizer.kt`, `TVWebViewClient.kt` 전수 UTF-8 유효성 및 한글 리터럴 무결성 검증 완료 (`True`).
