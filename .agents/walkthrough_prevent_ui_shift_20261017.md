# 결과 보고서: TV UI 상단 200px 밀림(Shift) 현상 원천 차단

## 1. 개요
YouTube TV 앱 사용 중 간헐적으로 화면 전체가 TV 상단 밖으로 200px 이상 밀려 올라가며 유튜브 로고와 상단 헤더가 잘려 보이는 문제를 정밀 분석하고, 네이티브 및 웹 계층 양쪽에서 원인을 원천 차단하였습니다.

---

## 2. 근본 원인 분석

1. **Android WebView 네이티브 스크롤 발생 (`mScrollY > 0`)**:
   - `TVWebView`에 네이티브 스크롤 차단 로직이 없어, 포커스가 화면 하단부로 이동하거나 특정 요소가 화면 갱신을 요청할 때 Android View 프레임워크가 뷰포트를 위로 밀어 올렸습니다.
   - YouTube TV는 CSS 내부 가상 스크롤을 사용하므로 네이티브 View의 `mScrollY`를 복원하지 못해 UI가 상단으로 영구 밀린 채 유지되었습니다.
2. **SoftInput Pan 모드 (`adjustPan`)**:
   - `AndroidManifest.xml`에 `windowSoftInputMode`가 미지정되어 기본값인 `adjustPan`으로 동작, 검색창이나 텍스트 입력 관련 포커스 시 윈도우 전체를 위로 패닝시켰습니다.
3. **`purgeQualityRoot()` 및 전역 MutationObserver 부작용**:
   - 이전 작업에서 추가된 `purgeQualityRoot()`가 50ms 주기 및 클래스 변경 감지마다 `body`에서 `app-quality-root`를 강제 제거하여, YouTube TV의 210개 TV 레이아웃 CSS 규칙과 충돌하고 불필요한 DOM 리플로우를 유발했습니다.

---

## 3. 수술적 정밀 수정 내역

1. **[TVWebView.kt](file:///E:/AI_Projects/%23%23%20YouTube%20TV%20for%20Android%20Clone/app/src/main/java/com/k2/youtubetv/webview/TVWebView.kt)**:
   - `scrollTo(x, y)` 오버라이드 $\rightarrow$ 항상 `super.scrollTo(0, 0)`으로 고정하여 어떤 상황에서도 네이티브 스크롤이 발생하지 않도록 잠금.
   - `computeScroll()`에서 `scrollX != 0 || scrollY != 0` 감지 시 즉각 `(0, 0)` 복원.
   - `overScrollBy(...)` $\rightarrow$ `false` 반환.
   - `overScrollMode = View.OVER_SCROLL_NEVER`, 수직/수평 스크롤바 비활성화.
2. **[AndroidManifest.xml](file:///E:/AI_Projects/%23%23%20YouTube%20TV%20for%20Android%20Clone/app/src/main/AndroidManifest.xml)**:
   - `MainActivity`에 `android:windowSoftInputMode="adjustNothing|stateAlwaysHidden"` 명시하여 입력 포커스로 인한 윈도우 프레임 이동 차단.
3. **[h5vcc_polyfill.js](file:///E:/AI_Projects/%23%23%20YouTube%20TV%20for%20Android%20Clone/app/src/main/assets/h5vcc_polyfill.js)**:
   - 불필요한 `purgeQualityRoot()` 및 `qualityObserver` 완전 제거.
   - CSS 규칙 상에서 이미 `.app-quality-root` 하위 선택자를 `!important`로 오버라이드하고 있으므로, `body`의 TV 네이티브 클래스 구조를 그대로 보존.
4. **[TVWebViewClient.kt](file:///E:/AI_Projects/%23%23%20YouTube%20TV%20for%20Android%20Clone/app/src/main/java/com/k2/youtubetv/webview/TVWebViewClient.kt)**:
   - `PATCH_VERSION = 8`로 상향하여 디스크 캐시 무효화 및 신규 스크립트 즉시 반영.

---

## 4. 검증 결과
- **릴리즈 빌드**: `./gradlew.bat assembleRelease` 성공 (BUILD SUCCESSFUL in 48s).
- **실기 TV 배포**: `adb install -r YT_TV_AC.apk` (5,204,695 bytes) 설치 완료 (`Success`).
- **렌더링 검증**: 실기 TV에서 상단 유튜브 로고, 검색창, 아바타 및 콘텐츠 영역이 정확한 1080p 고정 좌표에 안착되어 상단 밀림 없이 정상 동작함을 확인.
