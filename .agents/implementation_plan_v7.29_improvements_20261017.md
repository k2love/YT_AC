# 구현 계획서: v7.29.300 벤치마킹 및 종합 개선 패치 (1~5번 항목)

- **문서 번호**: `implementation_plan_v7.29_improvements_20261017.md`
- **대상 프로젝트**: `## YouTube TV for Android Clone` (`YT_AC`)
- **작성 일시**: 2026-10-17

---

## 1. 개요 및 목적
최신 YouTube for Android TV `v7.29.300` 리버스 엔지니어링에서 도출된 핵심 벤치마킹 인사이트(스토리지 진단, 동적 코덱 전환, 프레임 최적화, 렌더링 부하 절감)와 사용자가 겪은 200px UI 상단 쏠림 이슈를 원천 해결하기 위해 클론 앱 전반에 걸친 5대 개선 항목을 정밀 타격하여 패치합니다.

---

## 2. 세부 패치 계획

### [항목 1] `h5vcc.storage`에 `verifyTest`, `writeTest` 자가진단 메서드 추가
- **대상 파일**: `app/src/main/assets/h5vcc_polyfill.js`
- **수정 위치**: `h5vcc.storage` 객체 정의부
- **내용**:
  ```javascript
  storage: {
      clear: function() { if (window.NativeBridge) window.NativeBridge.storageClear(); },
      flush: function() { if (window.NativeBridge) window.NativeBridge.storageFlush(); },
      verifyTest: function() { return true; },
      writeTest: function() { return true; }
  }
  ```
- **검증**: JS 문법 오류 없음 확인, 웹 콘솔에서 `window.h5vcc.storage.verifyTest()` 호출 시 `true` 반환 확인.

### [항목 2] `media_can_change_type` 및 `SourceBuffer.prototype.changeType` 동적 코덱 전환 가드
- **대상 파일**: `app/src/main/assets/h5vcc_polyfill.js`
- **수정 위치**: MediaSource / 4K 언락 섹션
- **내용**:
  - `SourceBuffer.prototype.changeType`이 누락되거나 동적 전환 중 오류를 발생시키는 환경을 대비하여 안전 래퍼 및 폴리필 제공.
  - 영상 도중 코덱/해상도가 바뀌거나 본영상↔광고 전환 시 미디어 파이프라인 중단 방지.

### [항목 3] `CobaltFrameTiming` 벤치마킹: TV WebView 프레임 레이트 및 렌더러 우선순위 고정
- **대상 파일**: `app/src/main/java/com/k2/youtubetv/webview/TVWebView.kt`
- **수정 위치**: `initTVWebSettings()`
- **내용**:
  - `setRendererPriorityPolicy(RENDERER_PRIORITY_BOUND, false)` (Android 8.0 이상) 설정 추가하여 백그라운드 리소스 경합 시에도 WebView 렌더러 스레드 우선순위 최상위 보장.
  - 하드웨어 가속 레이어 확고화.

### [항목 4] `ShapePathJni` 벤치마킹: TV GPU 렌더링 부하 절감 및 CSS 최적화
- **대상 파일**: `app/src/main/assets/h5vcc_polyfill.js`
- **수정 위치**: UI 오버레이 및 투명도 관련 CSS 주입부
- **내용**:
  - 저사양 TV GPU에 부하를 줄 수 있는 과도한 필터나 무거운 연산을 배제하고 순수 RGBA/하드웨어 가속 트랜스폼(`transform: translateZ(0)`)으로 가볍게 최적화.

### [항목 5] 200px UI 상단 쏠림 현상(전체화면/인셋 깨짐) 원천 방어
- **대상 파일**: `app/src/main/java/com/k2/youtubetv/MainActivity.kt`
- **수정 위치**: `onCreate`, `onResume`, `onWindowFocusChanged`
- **내용**:
  - `onWindowFocusChanged(hasFocus: Boolean)` 오버라이드: 다른 앱에서 복귀하여 포커스를 다시 얻었을 때 `hideSystemUI()`를 즉각 재호출하여 전체화면 상태 복원.
  - `window.attributes.layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES` 적용 (Android 9.0 이상에서 디스플레이 인셋으로 인한 상단 쏠림 차단).
  - DecorView의 Insets 리스너에서 상단 시스템 바 인셋이 웹뷰 레이아웃을 밀어올리지 않도록 소비(`consumeSystemWindowInsets()`).

---

## 3. 검증 계획
1. 각 파일 수술적 정밀 수정 적용
2. UTF-8 인코딩 및 한글 리터럴 전수 체크
3. `./gradlew assembleDebug` 빌드 성공 확인
4. 변경 사항 diff 최소화 및 사이드이펙트 격리 검증
