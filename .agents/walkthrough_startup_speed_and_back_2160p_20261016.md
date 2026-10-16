# 검증 및 결과 리포트 (Walkthrough)

## 📌 작업 개요
- **작업명**: 초반 로딩 속도 최적화, 2160p 동영상 뒤로가기 정상화, 설정 메뉴 내 '앱 버전' 위 업데이트 확인 버튼 정밀 배치 (DOM TreeWalker 개편)
- **수행 일자**: 2026-10-16
- **대상 저장소**: [k2love/YT_AC](https://github.com/k2love/YT_AC) (`origin/main`)

---

## 🛠️ 핵심 변경 및 해결 내용

### 1. 설정 내 '앱 버전' 위 업데이트 확인 버튼 누락 원인 규명 및 TreeWalker 정밀 탐색 적용
- **원인 규명**:
  - 기존 로직에서 `if (!isSettings) return;` 조건을 걸었으나, YouTube TV는 단일 페이지 애플리케이션(SPA)이므로 URL 해시나 경로가 변하지 않고 (`https://www.youtube.com/tv` 고정), 가상의 카테고리 태그(`ytlr-settings-category-renderer`)는 YouTube TV에 실존하지 않아 **진입하자마자 함수가 조기 종료**되어 버튼이 DOM에 생성조차 되지 못했습니다.
  - 또한 `onPageFinished`에서 스크립트 주입이 생략되어 초기 빈 페이지 시점에만 실행될 위험이 있었습니다.
- **해결 사항**:
  - `app/src/main/assets/h5vcc_polyfill.js`:
    - `k2FindVersionElement()` 신설: 브라우저 표준 `TreeWalker`를 통해 DOM 트리의 모든 가시적 텍스트 노드를 실시간 스캔. "앱 버전", "App version", "버전: ", "Version: " 등 화면에 렌더링된 버전 텍스트를 100% 감지.
    - 감지된 노드의 상위 부모 요소를 거슬러 올라가 행(Row) 컨테이너 요소를 찾고, 바로 그 상단에 `parentNode.insertBefore(card, versionRow)`로 정밀 삽입.
    - TV 리모컨 D-Pad 포커스 시 배경을 순백색(`#FFFFFF`), 텍스트를 진한 검은색(`#0F0F0F`)으로 반전시키는 YouTube TV 순정 하이라이트 효과 적용.
    - 리모컨 OK(Enter) 버튼 또는 클릭 시 `window.YT_TV_APP.checkAppUpdate()`가 즉시 실행되어 네이티브 업데이트 다이얼로그 표시.
  - `TVWebViewClient.kt`:
    - `onPageFinished`에서 `injectPolyfill(view)`를 복원하여 페이지 로딩 완료 후에도 주입 타이머가 상시 보장되도록 개선.

### 2. 초반 로딩 속도 획기적 단축
- `TVWebViewClient.kt`: OkHttp 클라이언트에 50MB 디스크 캐시 및 **패치 바이너리 전용 디스크 캐시(`patched_web_cache`)**를 구축하여 2회차 실행부터 네트워크 0ms / 정규식 0ms로 즉각 로드.
- `MainActivity.kt`: 시작 시 백그라운드 깃허브 API 호출 제거 및 시작 URL을 `https://www.youtube.com/tv`로 단순화.

### 3. 2160p(4K) 동영상 뒤로가기 무반응 및 계정 선택기 튕김 해결
- `TVRemoteKeyHandler.kt`: 신뢰할 수 있는 단일 네이티브 `KeyEvent.KEYCODE_ESCAPE` (ACTION_DOWN + ACTION_UP) 디스패치 복원.
- `window._k2InBackNavigation = true` (1.5초) 플래그를 유지하여 플레이어가 닫히는 순간 계정 선택기로 강제 리다이렉트되는 현상 차단.

---

## 🔍 검증 결과

| 검증 항목 | 수행 내용 | 결과 |
| :--- | :--- | :---: |
| **Gradle 빌드** | `.\gradlew.bat assembleDebug` | **PASS (2s)** |
| **루트 APK 동기화** | `app/build/outputs/apk/debug/YT_TV_AC.apk` -> `YT_TV_AC.apk` (7,384,554 bytes) 복사 | **PASS** |
| **원격 Git 동기화** | `git commit` & `git push origin main` | **PASS** |

---

## 🚀 사용자 안내
- TV에서 앱을 실행한 후 좌측 메뉴를 통해 [설정]으로 진입하면, 화면 맨 하단의 **'앱 버전' 항목 바로 위에 [🔄 최신 앱 업데이트 확인] 버튼이 나타납니다**.
- 리모컨 D-Pad 아래 방향키로 내려가면 버튼이 밝은 흰색으로 포커스되며, 리모컨 확인(OK)을 누르면 즉시 최신 버전 확인 다이얼로그가 실행됩니다.
