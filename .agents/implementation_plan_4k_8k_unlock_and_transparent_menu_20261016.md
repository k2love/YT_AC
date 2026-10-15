# 구현 계획서: 4K/8K 화질 원천 언락, Kabuki 메뉴/컨트롤 투명화 및 옵션 뒤로가기 영상 멈춤 해결

## 1. 개요
사용자가 보고한 세 가지 핵심 결함을 역공학 분석을 바탕으로 완벽히 해결합니다:
1. **메뉴 및 컨트롤 여전히 불투명**: YouTube TV의 Cobalt/Kabuki 웹 프레임워크가 난독화된 44개의 선택자(`.Vdm04`, `.leUgff` 등)에 `-webkit-gradient`, `linear-gradient`를 사용하여 검은 상자를 그림. `kabuki.css` 인터셉션 및 투명 스타일 오버라이드로 해결.
2. **4K, 8K 언락 불가 (720p 고정 및 화질 메뉴 누락)**: `tv-player-ias.js` 내부의 해상도 필터 체인(`B3`, `k2`, `w$n`)이 720p 상한선을 강제하고 있음. `fetchAndPatchPlayerJs`에서 4320(8K) 패스스루로 서지컬 패치하여 해결.
3. **화질 메뉴 보고 뒤로가기 시 영상 멎음**: `TVRemoteKeyHandler.kt`에서 뒤로가기 누를 때 상황을 가리지 않고 무조건 `video.pause()`, `player.stopVideo()`를 호출하여 발생. 메뉴 열림 여부를 감지하여 메뉴만 닫고 영상 재생을 유지하도록 분기 처리.

---

## 2. 변경 대상 파일 및 세부 계획

### A. `app/src/main/java/com/k2/youtubetv/webview/TVWebViewClient.kt`
1. **`tv-player-ias.js` 4K/8K 화질 필터 무력화 패치**:
   - `B3`: `CF.prototype.B3=function(N){...}` -> `CF.prototype.B3=function(N){return new DA(0,4320,!1,"r");};`
   - `k2`: `function k2(N,L){...}` -> `function k2(N,L){return new DA(0,4320,!1,"o");}`
   - `w$n`: `function w$n(N,L){...}` -> `function w$n(N,L){return new DA(0,4320,!1,"w");}`
2. **`kabuki.css` 인터셉터 및 그라디언트 스크림 무력화**:
   - URL에 `/kabuki/_/ss/` 또는 `m=main`이 포함된 경우 가로채어 `linear-gradient(...)`, `-webkit-gradient(...)`, `radial-gradient(...)`를 `none`으로 교체하여 반환.

### B. `app/src/main/assets/h5vcc_polyfill.js` & `NativeAdSanitizer.kt`
- `getMasterCss()` 및 `splashFixCss`에 Kabuki 프레임워크 선택자 추가:
  `[class*="Vdm04"], [class*="Vdm04"]:before, [class*="Vdm04"]:after, .leUgff, .YHA8m, .dwgyh, .wTHb2c, .r4Pyib, .bel0Db, .q7Ygpb, .XpH8cb, .QvTwo, .jYycK`
  에 대해 `background: transparent !important; background-image: none !important; box-shadow: none !important; border: none !important;` 적용.

### C. `app/src/main/java/com/k2/youtubetv/remote/TVRemoteKeyHandler.kt`
- `handleBackAction`에서:
  - 팝업/설정 메뉴(`isMenuOpen`) 감지 시: 비디오 정지하지 않고 `Escape` 이벤트만 디스패치 후 `"HANDLED_MENU"` 리턴.
  - 메뉴가 없을 때만 비디오 정지 및 뒤로가기 실행.

---

## 3. 검증 계획
1. `.\gradlew.bat assembleDebug` 성공 확인.
2. APK 생성 및 크기 검증.
3. 소스 코드 UTF-8 인코딩 및 한글 리터럴 무결성 검증.
4. 결과 리포트 작성.
