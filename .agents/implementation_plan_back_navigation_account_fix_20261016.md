# 구현 계획서: 뒤로가기 시 계정 선택 화면 전환 원천 차단 및 안정적 뒤로가기 시스템 구축

## 1. 개요
동영상 시청 중 또는 홈 화면에서 리모컨의 뒤로가기(`KEYCODE_BACK` / `Escape`) 버튼을 누를 때, 메인 홈 화면으로 정상 복귀하지 않고 '누가 시청 중인가요?'(계정/프로필 선택 화면)로 튕기는 문제를 원천 해결합니다.

---

## 2. 문제 원인 정밀 역공학 분석
1. **연속된 다중 키 난사 (Machine-Gun Key Dispatches)**:
   - 기존 `TVRemoteKeyHandler.kt`에서 동영상 재생 중 뒤로가기 시, 한 번의 클릭에 `Escape`(down+up), `document Escape`, `GoBack`, `Backspace`, 그리고 네이티브 `KEYCODE_ESCAPE`(down+up)까지 무려 6~7개의 키 이벤트를 수 밀리초 안에 연속 발사했습니다.
   - YouTube TV(Kabuki) 라우터는 동기식 상태 전이를 수행하므로, 첫 번째 키로 플레이어가 닫힌 뒤 즉시 다음 키들이 연달아 도착하여 홈 화면 스택까지 팝(pop)되어 최하위 진입점인 '계정 선택 화면'까지 과속(Overshoot)하는 치명적 부작용이 발생했습니다.
2. **홈 화면에서 Escape 발사 오류**:
   - 이미 홈 화면에 도달한 상태에서도 뒤로가기 클릭 시 JS로 `Escape` 키를 document에 발사하고 있었습니다. YouTube Leanback SPA는 최상위 홈에서 `Escape`를 받으면 뷰 스택을 닫고 '계정 전환/선택'으로 진입합니다.
3. **YouTube TV의 `CAST_PROTECTION` 강제 계정 전환 로직 (`base.js`의 `_.n.Fg`)**:
   - `base.js`의 뒤로가기 라우터 메서드(`_.n.Fg`) 내부에는 `if (_.txa(this.history.Ca()) && _.As(_.H.get(_.Bs)))` 조건에 의해 `requestAccountSelectorCommand` (이벤트 트리거: `ACCOUNT_EVENT_TRIGGER_CAST_PROTECTION`)를 강제로 실행하도록 하드코딩되어 있습니다.
4. **`ACTION_UP` 미처리로 인한 안드로이드 시스템 백(Back) 누수**:
   - `handleKeyEvent`가 `ACTION_DOWN`만 소비하고 `ACTION_UP`은 `super.dispatchKeyEvent`로 흘려보내 안드로이드 기본 `onBackPressed()`나 WebView 자체 백스택이 추가로 트리거될 여지가 있었습니다.

---

## 3. 수술적 해결 방안

### 1단계: `TVWebViewClient.kt` 라우터 패치 (원천 방어)
- `fetchAndPatchJs`에 Kabuki 라우터 방어 패치 주입:
  1. `_.n.Fg` 내의 `ACCOUNT_EVENT_TRIGGER_CAST_PROTECTION` 조건문을 `!1`(false)로 비활성화하여 뒤로가기 시 계정 선택으로 분기되는 경로 차단.
  2. `_.kk`에서 `_.Zx.instance`(명령 디스패처)를 `window._k2CommandDispatcher`로 노출.
  3. `_.Zx.prototype.resolveCommand`에 가드를 설치하여, 뒤로가기 중(`window._k2InBackNavigation`)이거나 홈이 기로딩된 상태(`window._k2HasLoadedHome`)에서 `requestAccountSelectorCommand` / `restartToAccountSelectorCommand`가 들어오면 무조건 홈(`{browseEndpoint: {browseId: "default"}}`)으로 리다이렉트.

### 2단계: `h5vcc_polyfill.js` 보조 가드
- `window._k2InBackNavigation` 및 `window._k2HasLoadedHome` 상태 플래그 관리.
- 홈/시청 화면 진입 시 홈 로드 상태를 영구 마킹하여 이후 뒤로가기에 의한 계정 선택 전환 차단.

### 3단계: `TVRemoteKeyHandler.kt` 정밀 단일 이벤트로 재설계
- `ACTION_DOWN`뿐만 아니라 `ACTION_UP`도 완전히 소비하여 키 누수 원천 차단.
- 메뉴/다이얼로그 닫기: 1쌍의 단일 Escape 키(또는 close 버튼 클릭)만 전송하고 비디오 재생 유지.
- 동영상 종료 후 홈 복귀:
  - 비디오 정지 및 음소거.
  - `window._k2InBackNavigation = true` 활성화.
  - `window._k2CommandDispatcher.resolveCommand({browseEndpoint:{browseId:"default"}})`를 직접 호출하여 안전하고 즉각적인 홈 복귀 수행 (폴백: 단 1개의 Escape).
  - 머신건 키 난사 및 네이티브 중복 키 발사 전면 제거.
- 홈 화면:
  - WebView로 키를 일절 보내지 않음 (홈 화면이 팝되어 계정 선택으로 빠지는 현상 방지).
  - 2초 내 더블 클릭 시 `activity.finish()`로 앱 종료, 1회 클릭 시 "한 번 더 누르면 종료됩니다" 토스트 표시.

### 4단계: `MainActivity.kt` 연동 보강
- `onBackPressed()`를 오버라이드하여 시스템 레벨 백 제스처/신호 발생 시에도 `remoteKeyHandler`를 거치도록 안전장치 마련.

---

## 4. 검증 계획
1. `.\gradlew.bat assembleDebug` 빌드 성공 확인.
2. `YT_TV_AC.apk` 파일 갱신 및 Git 상태 점검.
3. 한국어 인코딩 깨짐 전수 점검.
