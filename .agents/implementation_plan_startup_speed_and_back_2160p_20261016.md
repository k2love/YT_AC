# 구현 계획서: 초반 로딩 속도 최적화, 2160p 뒤로가기 복구, 설정 내 업데이트 확인 버튼 배치

## 1. 개요
1. **초반 로딩 지연 해결**: 앱 시작 시 불필요한 네트워크 통신(자동 업데이트, `?launch=menu`)을 제거하고, OkHttp 디스크 캐시 및 패치된 스크립트/스타일시트 바이너리 캐시(`patched_web_cache`)를 구축하여 1초 이내 초고속 기동을 실현합니다.
2. **2160p 동영상 뒤로가기 정상화**: 2160p 등 고화질 동영상 재생 중 또는 메뉴 오버레이 상태에서 리모컨 뒤로가기 버튼이 무반응인 결함을 해결합니다. 브라우저가 신뢰하는 단일 네이티브 `KEYCODE_ESCAPE` 이벤트를 WebView 포커스 타깃에 정확히 전달하여 정상적으로 홈으로 빠져나오도록 합니다.
3. **설정 화면 내 '앱 버전' 바로 위 업데이트 확인 버튼 추가 및 자동 업데이트 제거**: 시작 시 자동 업데이트 알림을 제거하고, YouTube TV [설정] 메뉴 맨 하단의 '앱 버전' 바로 위에 리모컨 포커스가 가능한 [최신 앱 업데이트 확인] 버튼을 정밀 배치합니다.

---

## 2. 문제 분석 및 수술적 해결 방안

### 1) 초반 로딩 지연 원인 및 최적화 (`TVWebViewClient.kt`, `MainActivity.kt`)
- **원인**:
  - `TVWebViewClient`의 OkHttp 클라이언트에 캐시(`Cache`)가 없어 매 실행마다 `base.js`(1.1MB), `tv-player-ias.js`(2MB+), `kabuki.css`를 매번 원격 다운로드하고 수만 줄의 정규식 교체를 반복함.
  - 시작 시 불필요한 GitHub Commits API 호출(`checkForUpdates(false)`)과 `?launch=menu`로 인한 사이드바/계정 서랍 로딩 병목.
- **해결**:
  - OkHttp 50MB HTTP 디스크 캐시 적용.
  - 패치된 JS/CSS를 로컬 캐시 디렉터리(`patched_web_cache`)에 해시 기반으로 저장하여, 2회차 이후 실행 시에는 원격 다운로드 및 정규식 처리 없이 **1~2ms 만에 즉시 로컬 디스크에서 반환**.
  - 시작 URL을 `https://www.youtube.com/tv`로 단순화하고 시작 시 백그라운드 업데이트 확인 제거.

### 2) 2160p 동영상 뒤로가기 무반응 해결 (`TVRemoteKeyHandler.kt`)
- **원인**:
  - 지난 패치에서 가짜 JS `KeyboardEvent`(`isTrusted: false`)와 `window._k2CommandDispatcher.resolveCommand`를 시도했으나, Chromium Blink 엔진은 보안상 untrusted 이벤트를 무시하고, `movie_player`는 `resolveCommand`로 닫히지 않아 2160p 비디오에서 뒤로가기 신호가 증발함.
- **해결**:
  - 동영상 재생 중(`isVideoActive`) 또는 오버레이 열림(`found`) 시, 비디오 음소거/정지 및 포커스를 확보한 후 Android 네이티브의 **진짜(Trusted) `KeyEvent.KEYCODE_ESCAPE` (ACTION_DOWN + ACTION_UP)를 단 1회 정확히 `webView`에 디스패치**.
  - `window._k2InBackNavigation = true` (1.5초) 보호막으로 계정 선택기 전환 차단 유지.
  - 홈 화면에서는 키를 전달하지 않아 더블 클릭 종료 안정성 확보.

### 3) 설정 내 업데이트 확인 버튼 배치 (`h5vcc_polyfill.js`, `MainActivity.kt`)
- **원인 및 요구사항**:
  - 기존에는 설정 진입 시 맨 상단에 업데이트 카드가 삽입되었음.
  - 사용자는 자동 업데이트를 끄고, [설정] 화면 맨 하단의 '앱 버전' 바로 위에 버튼이 배치되기를 원함.
- **해결**:
  - `MainActivity.onCreate`에서 `appUpdateManager.checkForUpdates(false)` 완전 제거.
  - `h5vcc_polyfill.js`의 `k2InjectSettingsUpdateCard()` 개선:
    - 설정 목록 요소 중 텍스트에 `버전`, `version`, `build`, `빌드`가 포함된 요소를 탐색.
    - 해당 버전 요소 바로 위에(`versionItem.parentNode.insertBefore(card, versionItem)`) 버튼 삽입.
    - 리모컨 D-Pad 포커스 시 고대비 하이라이트 및 엔터 누를 시 `window.YT_TV_APP.checkAppUpdate()` 호출.
    - `checkAppUpdate()` 호출 시 `appUpdateManager.checkForUpdates(isManualCheck = true)` 즉각 실행.

---

## 3. 검증 계획
1. `.\gradlew.bat assembleDebug` 빌드 성공 확인.
2. 루트 `YT_TV_AC.apk` 갱신 및 Git 커밋/푸시.
3. 인코딩 및 한국어 출력 점검.
