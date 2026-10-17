# 구현 계획서: 앱 전체 UI 상단 200px 밀림(Shift) 현상 원천 차단

## 1. 문제 분석
- **증상**:
  - 정상 동작 중 간헐적으로 앱 전체 UI가 TV 상단 밖으로 200px 이상 밀려 올라가며 상단 유튜브 로고 및 헤더가 잘려 보이는 현상 발생.
  - 앱을 재시작하면 원상태로 복구됨.
- **근본 원인**:
  1. **Android WebView 네이티브 스크롤 오프셋 (`mScrollY > 0`)**:
     - `TVWebView`에 네이티브 스크롤 차단 로직(`scrollTo`, `requestChildRectangleOnScreen` 등)이 구현되어 있지 않아, 포커스가 화면 하단 영역으로 이동하거나 특정 요소가 포커스를 요청할 때 Android 프레임워크가 뷰포트를 위로 밀어 올림(`mScrollY` 발생).
     - YouTube TV는 CSS 내부 가상 스크롤을 사용하므로 네이티브 뷰의 `mScrollY`를 복원하지 못해 UI가 상단으로 영구 밀림.
  2. **Window SoftInput Pan (`adjustPan`)**:
     - `AndroidManifest.xml`에 `windowSoftInputMode`가 지정되지 않아 기본값인 `adjustPan`이 적용됨. 검색창 또는 입력 필드가 포커스를 받을 때 창 전체를 상단으로 200px 이상 밀어 올림.
  3. **`purgeQualityRoot()` 및 전역 MutationObserver의 레이아웃 부작용**:
     - 최근 추가된 `purgeQualityRoot()`가 50ms 주기 및 클래스 변경 감지마다 `body`에서 `app-quality-root`를 강제 제거하여, YouTube TV의 210개 TV 레이아웃 CSS 규칙과 충돌하고 불필요한 DOM 리플로우를 유발함.

---

## 2. 수술적 해결 방안

### A. `app/src/main/java/com/k2/youtubetv/webview/TVWebView.kt`
- 네이티브 스크롤 완전 잠금:
  - `scrollTo(x, y)`: 항상 `(0, 0)`으로 고정.
  - `computeScroll()`: `scrollX != 0 || scrollY != 0`인 경우 `scrollTo(0, 0)` 강제.
  - `overScrollBy()`: `false` 반환.
  - `requestChildRectangleOnScreen()`: `false` 반환하여 Android 프레임워크가 포커스 요소를 위해 뷰를 밀어 올리지 못하도록 차단.
  - `overScrollMode = View.OVER_SCROLL_NEVER`, 스크롤바 비활성화.

### B. `app/src/main/AndroidManifest.xml`
- `MainActivity`에 `android:windowSoftInputMode="adjustNothing|stateAlwaysHidden"` 추가하여 IME 또는 입력 포커스로 인한 윈도우 패닝 차단.

### C. `app/src/main/assets/h5vcc_polyfill.js`
- `purgeQualityRoot()` 및 `qualityObserver` 완전 제거.
- CSS 상에서 `.app-quality-root` 하위 선택자를 이미 `!important`로 오버라이드하고 있으므로, `body` 클래스를 임의 훼손하지 않고 순정 레이아웃 안정성 유지.

### D. `app/src/main/java/com/k2/youtubetv/webview/TVWebViewClient.kt`
- `PATCH_VERSION`: 7 $\rightarrow$ 8 (새 polyfill 즉시 갱신 반영).

---

## 3. 검증 계획
1. 소스 코드 빌드 성공 확인 (`.\gradlew.bat assembleRelease`).
2. 실기 TV 설치 및 정상 렌더링 확인.
3. 상단 로고 및 헤더의 200px 밀림 현상 완벽 방지 입증.
