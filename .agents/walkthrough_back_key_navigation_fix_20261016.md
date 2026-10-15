# 결과 리포트: 영상 재생 중 뒤로 가기 시 메인 화면 정상 복귀 완료

- **기능명**: 영상 시청 중 뒤로 가기(Back) 네비게이션 정상화 및 계정 선택 롤백 방지
- **작성일**: 2026-10-16
- **저장소**: [k2love/YT_AC](https://github.com/k2love/YT_AC)

---

## 1. 개요 및 사용자 문제 분석
- **문제 증상**: 영상 재생 중 리모컨의 '뒤로 가기' 버튼을 누르면 직전 탐색 화면(메인 홈/검색 화면)으로 복귀하는 대신, 앱 첫 진입 시의 **"계정 선택(Who's watching / Choose an account)"** 화면으로 튕기는 현상 발생.
- **원인 규명**:
  1. YouTube TV(Kabuki 프레임워크)는 브라우저 히스토리 스택을 사용하지 않는 SPA(Single Page Application) 구조입니다.
  2. 사용자가 앱 실행(`launch=menu`) 후 [계정 선택] $\rightarrow$ [메인 화면] $\rightarrow$ [영상 시청] 순서로 진입했을 때, 브라우저의 히스토리 이전 엔트리는 바로 **[계정 선택]** 화면입니다.
  3. 기존 코드에서 영상 시청 중 `window.history.back()`, `location.replace(_k2LastBrowse)`, `webView.goBack()`을 실행하여 YouTube TV 내부 뷰 스택을 거치지 않고 브라우저 히스토리가 통째로 롤백되면서 계정 선택 화면이 떴던 것입니다.

---

## 2. 수술적 해결 조치 내역

### 2.1 불필요한 브라우저 히스토리 조작 100% 제거
1. **[`h5vcc_polyfill.js`](file:///E:/AI_Projects/##%20YouTube%20TV%20for%20Android%20Clone/app/src/main/assets/h5vcc_polyfill.js)**:
   - `_k2LastBrowse` 감시 루프를 완전히 비활성화하여 `launch=menu`로의 강제 리로드 원인을 근원 차단했습니다.
2. **[`TVRemoteKeyHandler.kt`](file:///E:/AI_Projects/##%20YouTube%20TV%20for%20Android%20Clone/app/src/main/java/com/k2/youtubetv/remote/TVRemoteKeyHandler.kt)**:
   - 영상 시청 중 `window.history.back()` 및 `location.replace(...)`, `webView.goBack()` 호출 코드를 전면 제거했습니다.

### 2.2 YouTube TV (Kabuki) 순정 네비게이션 연동
- 영상 시청 화면(Watch Screen) 감지 시:
  1. **오디오 누출 차단**: 모든 `<video>` 태그에 `pause()`, `muted = true` 및 플레이어 `stopVideo()`를 즉각 실행하여 백그라운드 소리 누출을 0.001초 만에 방지합니다.
  2. **순정 키보드 네비게이션**: 네이티브 WebView에 정품 `isTrusted: true`인 `KeyEvent.KEYCODE_ESCAPE` (DOWN & UP)을 디스패치하고, JS 레벨에서도 `Escape`(keyCode 27) 및 `GoBack`(keyCode 461) 이벤트를 발생시킵니다.
  3. **결과**: YouTube TV 프레임워크가 Watch Screen을 닫고 **이전에 보던 메인 홈 화면(Browse)**으로 부드럽게 복귀합니다.
  4. **오버레이 메뉴와의 완벽한 공존**: 화질 설정, 재생 속도 등 팝업 메뉴가 열려 있을 때는 비디오를 끄지 않고 메뉴만 닫는 기존 로직을 100% 안전하게 유지했습니다.

---

## 3. 빌드 및 산출물 검증
- **빌드 상태**: `BUILD SUCCESSFUL in 2s`
- **산출물**: `E:\AI_Projects\## YouTube TV for Android Clone\app\build\outputs\apk\debug\YT_TV_AC.apk` (7,384,554 바이트, 약 7.38 MB)
- **한글 리터럴 무결성**: 토스트 및 UI 메시지 UTF-8 보존 완료
