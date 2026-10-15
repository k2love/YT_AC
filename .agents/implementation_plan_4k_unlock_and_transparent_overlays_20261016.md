# 구현 계획서: 4K 해상도 강제 다운그레이드 언락, 완전 투명 로고/컨트롤 적용 및 사후 광고 원천 박멸

## 1. 개요
사용자가 제기한 3가지 핵심 결함을 기술적으로 정밀 타격하여 완벽히 해결합니다.
1. **2160p 이상의 영상이 720p로 강제 다운그레이드되는 현상**:
   - WebView의 논리 해상도(`screen.width = 1280`)와 1080p 전용 핑거프린트(`eureka`), `MediaSource.isTypeSupported`의 보수적 판단으로 인해 유튜브 플레이어가 720p로 클램핑함.
   - 4K 정식 핑거프린트(`sabrina`), `screen.width = 3840`, `screen.height = 2160`, `MediaSource.isTypeSupported` VP9/AV1 4K 언락으로 해결.
2. **로고, 컨트롤 메뉴, 영상 제목 등의 검정 불투명 배경 잔존**:
   - 유튜브 원본의 `#loader` 이미지 자체가 불투명 배경을 가진 Indexed PNG 파일이었음.
   - 이를 완벽한 알파 투명 채널이 포함된 Data URI(`splash_logo_transparent.png`)로 전면 교체.
   - WebView 컴포지터가 `linear-gradient`를 불투명 검정 박스로 그리는 현상을 방지하기 위해 모든 컨트롤/타이틀 오버레이를 순수 투명(`background: transparent !important; background-image: none !important;`)으로 강제하고 부드러운 텍스트 섀도우를 부여.
3. **영상 시작 1~2초 후 강제 광고 출현**:
   - 플레이어가 비동기 하트비트/미드롤 응답 또는 초기 데이터의 잔존 `adBreakHeartbeatParams`를 읽어 광고 모드로 진입.
   - `JSON.parse` 훅에서 광고 스케줄 관련 파라미터 전수 제거, `TVWebViewClient`에서 미드롤/애드브레이크 요청 204 No Content 드롭, 초고속(15ms) `instantAdKiller`로 0프레임 무력화.

---

## 2. 변경 대상 파일 및 상세 내용

### A. `.agents/transparent_logo_b64.txt` 활용
- 이 파일에는 43,554 바이트 크기의 순수 투명 RGBA PNG의 Base64 문자열이 들어 있음.
- 이를 `h5vcc_polyfill.js` 및 `NativeAdSanitizer.kt`의 CSS 스타일 `#loader`에 `background-image: url("data:image/png;base64,...") !important;`로 삽입.

### B. `app/src/main/assets/h5vcc_polyfill.js`
1. **4K Display & Codec Unlock**:
   - `screen.width = 3840`, `screen.height = 2160`, `screen.availWidth = 3840`, `screen.availHeight = 2160` 게터 오버라이드.
   - `window.devicePixelRatio = 2.0` 오버라이드.
   - `MediaSource.isTypeSupported` 패치: `vp9`, `vp09`, `av01` 쿼리에 대해 무조건 `true` 반환.
   - `h5vcc.system.buildFingerprint`: `"google/sabrina/sabrina:12/STTE.231215.005/11324838:user/release-keys"` (Chromecast with Google TV 4K 정식 핑거프린트)로 갱신.
2. **투명 로고 및 컨트롤 투명화 CSS**:
   - `#loader`의 `background-image`에 투명 로고 Base64 주입.
   - 컨트롤, 타이틀, 스크림, 그라디언트 클래스에 `background: transparent !important; background-image: none !important; box-shadow: none !important;` 적용.
   - 텍스트 가독성을 위한 `text-shadow` 보존.
3. **Zero-Tolerance Ad Killer 강화**:
   - `instantAdKiller`를 15ms 주기로 실행.
   - `video` 태그 재생 감시 및 광고 발생 시 즉시 건너뛰기.

### C. `app/src/main/java/com/k2/youtubetv/webview/NativeAdSanitizer.kt`
- 초기 HTML 인라인 `<style id="zero-ad-master-style">` 내에 투명 로고 Base64 및 투명화 CSS를 동일하게 주입하여, 페이지 로드 최초 0.1초부터 검정 배경 없이 투명 로고가 뜨도록 보장.

### D. `app/src/main/java/com/k2/youtubetv/webview/TVWebViewClient.kt`
- `/youtubei/v1/player/ad_break`, `/get_midroll_info`, `/pagead/`, `&oad=` 등 차단 패턴 재확인 및 철통 차단 유지.

---

## 3. 검증 계획
1. `.\gradlew.bat assembleDebug` 실행하여 빌드 에러 없이 성공하는지 확인.
2. 생성된 APK 파일 크기 및 산출물 경로 확인.
3. 소스 코드 내 한글 깨짐 여부 전수 검사.
4. 결과 보고서(`walkthrough_...md`) 작성.
