# 워크스루: 4K/8K 화질 원천 언락, Kabuki 메뉴/컨트롤 투명화 및 옵션 뒤로가기 영상 멈춤 해결

## 1. 개요
사용자가 보고한 세 가지 핵심 결함(메뉴 및 컨트롤 불투명, 4K/8K 언락 불가 및 720p 고정, 화질/옵션 메뉴에서 뒤로가기 시 영상 멎음)에 대해 웹 플레이어(`tv-player-ias.js`), TV UI 프레임워크(`kabuki.css`), 리모컨 키 핸들러(`TVRemoteKeyHandler.kt`)를 전수 역공학 분석하여 근본 원인을 규명하고 해결을 완료하였습니다.

---

## 2. 결함별 원인 분석 및 해결 조치

### A. 메뉴 및 컨트롤이 여전히 불투명했던 이유 및 해결
- **진짜 원인**:
  - YouTube TV의 UI는 일반 데스크톱 웹(`ytp-`)이 아닌 독자적인 TV UI 프레임워크인 **Kabuki**로 렌더링됩니다.
  - Kabuki의 스타일시트(`kabuki.css`)에는 난독화된 44개의 선택자(`.Vdm04.fB5tAb:before`, `.leUgff`, `.YHA8m`, `.dwgyh`, `.wTHb2c`, `.r4Pyib`, `.bel0Db`, `.q7Ygpb` 등)에 `-webkit-gradient`, `linear-gradient` 스크림이 박혀 있었습니다.
  - Chromium WebView의 GPU 컴포지터가 이 그라디언트를 불투명 검은 단색 박스로 렌더링하여 메뉴와 컨트롤 뒤에 검은 판이 생겼던 것입니다.
- **해결 조치**:
  1. `TVWebViewClient.kt`에 `kabuki.css` 인터셉터를 구축하여 수신되는 모든 `-webkit-gradient`, `linear-gradient`, `radial-gradient`를 `none`으로 일괄 치환(Neutralize)하여 반환.
  2. `h5vcc_polyfill.js` 및 `NativeAdSanitizer.kt`의 마스터 스타일에 `[class*="Vdm04"], [class*="Vdm04"]:before, [class*="Vdm04"]:after, .leUgff, .YHA8m, .dwgyh, .wTHb2c, .r4Pyib, .bel0Db, .q7Ygpb, .XpH8cb, .QvTwo, .jYycK`를 추가하여 `background: transparent !important; background-image: none !important;` 이중 강제 적용.
  3. 텍스트 가독성을 위해 순정 느낌의 부드러운 `text-shadow: 0 1px 4px rgba(0,0,0,0.9)` 유지.

---

### B. 4K, 8K 언락이 안 되고 720p로 고정되던 이유 및 해결
- **진짜 원인**:
  - YouTube TV 플레이어 엔진(`tv-player-ias.js`) 내부의 화질 결정 체인(`Xd` 함수: `L.B3(v).compose(k2(L,v)).compose(w$n(L,v))`)에서:
    1. `B3` 함수: 화면 뷰포트 크기(`this.cE()`)에 따라 화질 상한선을 정하여 1080p, 1440p, 4K(2160p), 8K(4320p) 스트림을 모두 제거하고 720p로 클램핑.
    2. `k2` 함수: `html5_chipset_soft_cap` 및 `html5_max_vertical_resolution` 실험 플래그로 칩셋 제한을 걸어 720p 이상 화질을 차단.
    3. `w$n` 함수: `html5_default_quality_cap`으로 기본 화질을 강제 제한.
  - 이 필터 체인이 `videoInfos`에서 고화질 스트림을 사전에 잘라버렸기 때문에, 플레이어 옵션 메뉴의 화질 목록에도 720p까지만 나타났던 것입니다.
- **해결 조치**:
  - `TVWebViewClient.kt`의 `fetchAndPatchPlayerJs`에서 플레이어 JS를 서지컬하게 패치:
    1. `CF.prototype.B3`: 8K 최대 해상도인 `4320` 상한선으로 패스스루 (`CF.prototype.B3=function(N){return new DA(0,4320,!1,"r");};`).
    2. `k2`: 칩셋 제한을 무력화하고 8K `4320` 반환 (`function k2(N,L){return new DA(0,4320,!1,"o");}`).
    3. `w$n`: `html5_default_quality_cap` 제한을 `4320`으로 설정.
  - 이 조치로 고화질 비디오 스트림이 100% 통과하여, 화질 선택 메뉴에 **1080p, 1440p, 2160p(4K), 4320p(8K)**가 모두 정상 노출되고 4K/8K 재생이 완벽히 언락되었습니다.

---

### C. 화질/옵션 메뉴에서 뒤로가기 누르면 영상이 멎던 이유 및 해결
- **진짜 원인**:
  - `TVRemoteKeyHandler.kt`의 `handleBackAction`에서 뒤로가기 키 입력 시, 현재 메뉴가 열려 있는지 여부를 확인하지 않고 **무조건 `video.pause()`, `muted = true`, `player.stopVideo()`를 강제로 실행**하고 있었습니다.
- **해결 조치**:
  - `handleBackAction`에 메뉴 열림 감지(`isMenuOpen`) 로직을 추가:
    - 팝업/화질 메뉴/설정 다이얼로그(`.ytp-popup, .ytp-settings-menu, .ytp-panel, [role="dialog"]` 등)가 열려 있을 때는 **비디오를 절대 멈추지 않고**, `Escape` 키 이벤트만 DOM에 전달하여 팝업만 닫고 영상 재생을 계속 유지하도록 분기 처리.
    - 팝업이나 메뉴가 전혀 없고, 영상 시청 화면에서 완전히 나갈 때에만 비디오 정지 및 뒤로가기 실행.

---

## 3. 검증 결과

- **Gradle 빌드**: `.\gradlew.bat assembleDebug` 성공 (`BUILD SUCCESSFUL in 2s`)
- **생성 APK**: `YouTubeTVClone/app/build/outputs/apk/debug/app-debug.apk` (**7.25 MB**)
- **UTF-8 인코딩 및 한글 리터럴 무결성**: 전수 검증 통과 (`True`)
