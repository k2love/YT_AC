# [인수인계 문서] YouTube for Android TV 클론 및 완벽 제로-애드(Zero-Ad) 프로젝트

> **작성 일시**: 2026-10-16  
> **프로젝트 루트**: `E:\AI_Projects\## REA (Reverse Engineering Anything)`  
> **안드로이드 프로젝트 위치**: `E:\AI_Projects\## REA (Reverse Engineering Anything)\YouTubeTVClone`  
> **현재 빌드 산출물**: `YouTubeTVClone/app/build/outputs/apk/debug/app-debug.apk` (약 7.25 MB)  
> **빌드 커맨드**: `cd YouTubeTVClone; .\gradlew.bat assembleDebug`

---

## 1. 프로젝트 목표 및 개요
- **목표**: YouTube for Android TV (v7.28.300) 오리지널 Cobalt 앱과 100% 동일한 순정 UI 및 알고리즘을 구현하되, **광고(대문 머스트헤드, 인피드 스폰서, 사전/사후 1~2초 강제광고, 백그라운드 광고음)를 원천 차단**하고 **4K(2160p) 및 8K(4320p) 고화질을 완벽히 언락**한 클린룸 독립 Android TV 앱 완성.
- **구현 방식**: 오리지널 Cobalt 엔진의 Starboard C++ 네이티브 계층(`H5VCC`, `PlatformService`, `Starboard SyncAuth`)을 리버스 엔지니어링하여 Kotlin/JavaScript Polyfill로 완벽 에뮬레이션하고, Android WebView 기반의 순정 고성능 웹앱(`https://www.youtube.com/tv`)을 구동.

---

## 2. 프로젝트 핵심 아키텍처 및 소스 파일 위치

| 구분 | 파일 경로 | 주요 역할 및 핵심 로직 |
| :--- | :--- | :--- |
| **Main Activity** | `YouTubeTVClone/app/src/main/java/com/k2/youtubetv/MainActivity.kt` | 앱 라이프사이클, Immersive Sticky 풀스크린, 리모컨 키 분기, WebView 초기화 및 URL 로드 |
| **WebView Core** | `YouTubeTVClone/app/src/main/java/com/k2/youtubetv/webview/TVWebView.kt` | Cobalt 전용 User-Agent, 하드웨어 가속, `DOCUMENT_START_SCRIPT` 초기 바인딩, 포커스 제어 |
| **Native Client** | `YouTubeTVClone/app/src/main/java/com/k2/youtubetv/webview/TVWebViewClient.kt` | - 광고 비콘/미드롤/`player/ad_break` 즉시 204 차단<br>- 순수 광고 비디오 스트림(`adformat=`, `&oad=`) 204 차단<br>- `tv-player-ias.js` 패치 (광고 체크 함수 무력화, **4K/8K 화질 필터 무제한 언락**)<br>- `kabuki.css` 인터셉트 (검은 박스를 만드는 **그라디언트 스크림을 `none`으로 원천 무력화**)<br>- HTML 동기 인라인 살균(`NativeAdSanitizer`) |
| **HTML/JSON Sanitizer** | `YouTubeTVClone/app/src/main/java/com/k2/youtubetv/webview/NativeAdSanitizer.kt` | - `ytInitialData`, `ytInitialPlayerResponse` 내 광고 슬롯 재귀 삭제<br>- 원본 불투명 `#loader` CSS 블록을 **완전 투명 RGBA Data URI로 수술적 치환**<br>- 최상단 `<head>`에 마스터 투명 CSS 및 인라인 스크립트 주입 |
| **Remote Handler** | `YouTubeTVClone/app/src/main/java/com/k2/youtubetv/remote/TVRemoteKeyHandler.kt` | - D-Pad 및 미디어 키 제어<br>- **화질/설정 메뉴 열림 감지(`isMenuOpen`)**: 메뉴가 열려있을 땐 비디오를 멈추지 않고 메뉴만 닫기(`HANDLED_MENU`)<br>- 영상 시청 종료 시에만 오디오 누출 킬스위치 실행 후 뒤로가기<br>- 최상단 홈 화면 더블 백 종료 |
| **H5VCC Polyfill** | `YouTubeTVClone/app/src/main/assets/h5vcc_polyfill.js` | - Cobalt Starboard `h5vcc.system`, `platformService` 브릿지<br>- **전역 `JSON.parse` 훅**: 파싱되는 모든 객체에서 `adPlacements`, `adSlots`, `playerAds`, `adBreakHeartbeatParams` 물리적 `delete`<br>- `fetch` / `XHR` 광고 차단<br>- 4K 디스플레이 규격 오버라이드 (`screen.width=3840`, `screen.height=2160`, `devicePixelRatio=2.0`)<br>- `MediaSource.isTypeSupported` VP9/AV1 언락<br>- 50ms 주기 `instantAdKiller` |
| **Transparent Logo** | `YouTubeTVClone/app/src/main/assets/transparent_logo_b64.txt` | 오리지널 회색 불투명 배경(`RGB(40,40,40)`)을 제거하고 알파=0 완전 투명으로 변환한 43KB Base64 Data URI |

---

## 3. 리버스 엔지니어링을 통해 해결된 핵심 결함 히스토리

### 1) 앱 시작 시 유튜브 로고 뒤에 검정/회색 네모 상자가 남던 현상
- **원인**: `https://www.youtube.com/tv`의 `#loader` CSS에 박힌 원본 이미지가 투명 PNG가 아니라 **배경이 `RGB(40,40,40)`으로 가득 찬 1984x444 크기의 불투명 Indexed PNG**였음. CSS로 아무리 `background-color: transparent`를 주어도 이미지 파일 자체가 불투명했기 때문에 네모가 보였던 것.
- **해결**: Python PIL로 완전 투명 RGBA PNG로 변환하여 Data URI를 생성하고, `NativeAdSanitizer.kt`에서 원본 HTML 파싱 시 `#loader` CSS 블록을 직접 교체함.

### 2) 4K/8K 영상이 720p로 강제 다운그레이드되고 화질 옵션에 720p까지만 나오던 현상
- **원인**: 플레이어 엔진(`tv-player-ias.js`) 내부의 화질 결정 체인(`Xd` 함수: `L.B3(v).compose(k2(L,v)).compose(w$n(L,v))`)에서:
  - `B3`: 화면 뷰포트 크기를 보고 720p 초과 스트림을 삭제하여 클램핑.
  - `k2`: `html5_chipset_soft_cap` 및 `html5_max_vertical_resolution` 플래그로 칩셋 제한을 걸어 720p로 절단.
  - `w$n`: `html5_default_quality_cap`으로 기본 화질 제한.
- **해결**: `TVWebViewClient.kt`의 `fetchAndPatchPlayerJs`에서 `B3`와 `k2`가 항상 8K 최대 해상도인 `4320`을 반환하도록 서지컬 패치하여 고화질 스트림을 100% 보존.

### 3) 메뉴 및 컨트롤 뒷배경이 검은 불투명 상자로 보이던 현상
- **원인**: YouTube TV는 데스크톱(`ytp-`)이 아닌 독자적인 **Kabuki** 프레임워크를 사용하며, 스타일시트(`kabuki.css`) 내의 44개 난독화 선택자(`.Vdm04...:before`, `.leUgff`, `.YHA8m` 등)에 `-webkit-gradient`, `linear-gradient` 스크림이 정의되어 있음. Android TV WebView GPU 컴포지터가 이 그라디언트를 불투명 검은 단색 상자로 렌더링함.
- **해결**: `TVWebViewClient.kt`에서 `kabuki.css` 요청을 인터셉트하여 모든 그라디언트를 `none`으로 원천 무력화하고, 마스터 스타일에 Kabuki 클래스 투명 규칙을 주입.

### 4) 화질/설정 메뉴를 보고 뒤로가기를 누르면 영상이 멎어버리던 현상
- **원인**: `TVRemoteKeyHandler.kt`에서 뒤로가기 키 입력 시 현재 메뉴 열림 상태를 확인하지 않고 무조건 `video.pause()`, `player.stopVideo()`를 호출하여 발생.
- **해결**: `isMenuOpen` 감지 로직을 추가하여 메뉴나 팝업이 열려 있을 때는 비디오를 멈추지 않고 `Escape` 키 이벤트만 전달하여 메뉴만 닫고 영상 재생을 유지함.

### 5) 영상 재생 시작 1~2초 후 튀어나오는 강제 광고
- **원인**: 플레이어가 재생 직후 비동기로 하트비트 세션(`adBreakHeartbeatParams`) 및 미드롤 정보(`/player/ad_break`)를 호출하여 광고를 삽입.
- **해결**: `h5vcc_polyfill.js`의 `JSON.parse` 훅에서 파싱되는 모든 InnerTube 객체에서 광고 스케줄 객체 물리적 `delete` + `TVWebViewClient`에서 미드롤 요청 204 드롭 + 50ms 주기 `instantAdKiller`로 무력화.

---

## 4. 빌드 및 테스트 방법
```bash
# 1. 안드로이드 프로젝트 디렉토리로 이동
cd "E:\AI_Projects\## REA (Reverse Engineering Anything)\YouTubeTVClone"

# 2. 디버그 APK 빌드 (약 2~3초 소요)
.\gradlew.bat assembleDebug

# 3. APK 파일 확인
# 경로: YouTubeTVClone\app\build\outputs\apk\debug\app-debug.apk (약 7.25 MB)

# 4. 안드로이드 TV 기기 또는 에뮬레이터에 설치
adb install -r app\build\outputs\apk\debug\app-debug.apk
```

---

## 5. 제미나이 웹에서 이어받아 점검 및 발전시킬 과제 (Next Tasks)
1. **실기기(Android TV / Fire TV / Chromecast with Google TV) 현장 테스트**:
   - 4K(2160p) 및 8K 영상 재생 시 화질 옵션 목록에 `2160p 4K`, `1440p`, `1080p`가 정상 노출되고 실제 버퍼링 없이 매끄럽게 재생되는지 확인.
   - 재생 중 아래 방향키 또는 엔터키로 컨트롤 바를 띄웠을 때 뒤에 시커먼 박스 없이 완전히 투명한 배경으로 뜨는지 확인.
   - 화질 선택 팝업을 열었다가 리모컨 `뒤로가기`를 눌렀을 때 영상이 멈추지 않고 팝업만 깔끔하게 닫히는지 확인.
2. **구글 계정 로그인(SyncAuth) 안정성 점검**:
   - `SyncAuthCredentialService.kt` 및 `GoogleAuthManager.kt`를 통한 기기 구글 계정 동기화 작동 상태 확인.
3. **음성 검색(Voice Search) 연동 지원**:
   - 리모컨 마이크 버튼을 눌렀을 때 Cobalt 음성 검색 인터페이스와의 연동 고도화.
