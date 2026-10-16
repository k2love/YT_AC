# Walkthrough: 뒤로가기 시 계정 선택 화면 전환 원천 차단 및 안정적 뒤로가기 시스템 구축

YouTube TV for Android TV 클론 앱(`YT_TV_AC`)에서 동영상 재생 중 또는 홈 화면에서 뒤로가기 버튼을 누를 때, 메인 화면 대신 '누가 시청 중인가요?'(계정 선택 화면)로 튕기던 근본 결함을 정밀 역공학을 통해 원인을 밝혀내고 완전히 해결했습니다.

---

## 1. 근본 원인 분석 (Root Causes)

1. **머신건 키 난사 (Machine-Gun Key Dispatches)**:
   - 기존 코드에서는 동영상 시청 중 뒤로가기 시 `Escape`(down+up), `document Escape`, `GoBack`, `Backspace`, 그리고 안드로이드 네이티브 `KEYCODE_ESCAPE`(down+up)까지 6~7개의 키를 수 밀리초 내에 연속 발사했습니다.
   - 단일 페이지 앱(SPA)인 YouTube TV는 첫 번째 키로 플레이어가 닫힌 후, 남아있던 키들이 즉시 연속 처리되면서 홈 화면 스택마저 팝(pop)되어 최하위 진입점인 계정 선택 화면까지 과속(Overshoot)하게 되었습니다.
2. **홈 화면에서 Escape 발사 오류**:
   - 이미 홈 화면에 도달한 상태에서도 document에 `Escape` 키를 전달하여, YouTube Leanback이 뷰 스택을 닫고 계정 전환 화면을 띄우는 원인이 되었습니다.
3. **YouTube TV 라우터의 Cast Protection 강제 계정 전환 로직 (`base.js`의 `_.n.Fg`)**:
   - YouTube TV 순정 코드 내부에는 뒤로가기(`_.n.Fg`) 실행 시 `if (_.txa(...) && _.As(...))` 조건에 의해 `requestAccountSelectorCommand`(`ACCOUNT_EVENT_TRIGGER_CAST_PROTECTION`)를 호출하여 계정 선택기를 강제로 띄우는 메커니즘이 내장되어 있었습니다.
4. **`ACTION_UP` 미처리로 인한 안드로이드 시스템 백(Back) 누수**:
   - `handleKeyEvent`가 `ACTION_DOWN`만 처리하고 `ACTION_UP`은 `super.dispatchKeyEvent`로 통과시켜 안드로이드 액티비티/웹뷰 기본 뒤로가기 로직이 중복 발동했습니다.

---

## 2. 수술적 해결 내용

### 1) `TVWebViewClient.kt` 라우터 가드 주입
- `fetchAndPatchJs`를 통해 `base.js`에 세 가지 핵심 패치 주입:
  1. **Cast Protection 무력화**: `_.n.Fg`의 `ACCOUNT_EVENT_TRIGGER_CAST_PROTECTION` 트리거 조건을 무조건 `false`(`!1`)로 만들어 뒤로가기 시 계정 선택 분기를 원천 차단.
  2. **명령 디스패처 노출**: `_.kk`에서 `window._k2CommandDispatcher = _.Zx.instance`를 노출하여 홈 화면 복귀를 직접 지시할 수 있도록 연동.
  3. **`resolveCommand` 가드**: 뒤로가기 도중(`_k2InBackNavigation`)이거나 홈이 로드된 상태(`_k2HasLoadedHome`)에서 `requestAccountSelectorCommand` 또는 `restartToAccountSelectorCommand`가 유입되면 무조건 홈(`{browseEndpoint: {browseId: "default"}}`)으로 자동 전환.

### 2) `h5vcc_polyfill.js` 상태 추적
- `window._k2InBackNavigation` 및 `window._k2HasLoadedHome` 플래그 관리 추가.
- 사용자가 홈 화면이나 동영상 재생 화면에 한 번이라도 도달하면 `_k2HasLoadedHome = true`로 고정하여 이후 어떤 경우에도 계정 선택기로 회귀하지 않도록 보호.

### 3) `TVRemoteKeyHandler.kt` 정밀 단일 이벤트로 재설계
- **키 난사 제거**:
  - 메뉴 닫기: 1쌍의 단일 `Escape` 키(또는 close 버튼 클릭)만 발사하여 비디오 재생 끊김 없이 오버레이만 닫음.
  - 비디오 종료: 비디오 음소거/정지 후 `window._k2CommandDispatcher.resolveCommand({browseEndpoint:{browseId:"default"}})`를 직접 호출하여 안전하고 깨끗하게 홈 화면으로 복귀.
- **홈 화면 보호**:
  - 홈 화면에서는 WebView로 키를 일절 전달하지 않음.
  - 2초 내 더블 클릭 시 `activity.finish()`로 앱 종료, 1회 클릭 시 "뒤로 가기 버튼을 한 번 더 누르면 종료됩니다." 토스트 표시.
- **`ACTION_UP` 완전 소비**:
  - `KEYCODE_BACK` / `KEYCODE_ESCAPE`의 `ACTION_UP`도 함께 소비하여 시스템 백 이벤트 누수 차단.

### 4) `MainActivity.kt` `onBackPressed` 연동
- 액티비티의 `onBackPressed()`를 오버라이드하여 리모컨 핸들러의 `handleBackFromActivity()`로 일원화.

---

## 3. 검증 결과

- Gradle 빌드: `.\gradlew.bat assembleDebug` 성공 (`BUILD SUCCESSFUL in 3s`).
- 최신 빌드 산출물 동기화: 루트 `YT_TV_AC.apk` 갱신 완료 (`7,384,554 bytes`).
- 모든 파일의 한국어 문자열 및 인코딩 정상 보존 확인.
