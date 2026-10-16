# 작업 리포트: browse 뒤로가기 레일 포커스 + 피드백 pulls 텍스트 + 홀드 반복 가드

> **작업 일시**: 2026-10-16 (후속)
> **검증**: 실기기(192.168.100.121) + CDP DOM 프로브 + node 하네스 28/28

---

## 1. 증상별 원인 및 수정

### (1) 영상 그리드에서 뒤로가기 → 종료 안내만 표시
- **원인 2개**:
  1. browse 진입 시 뒤로가기가 `ROOT_HOME`으로 직행해 종료 토스트를 띄웠음.
     네이티브 동작(레일로 포커스 이동)이 빠져 있었음.
  2. 더 심각: 그리드 프리뷰 잔여물(`currentTime`/`readyState` 잔존)이 모든
     browse-뒤로가기를 영상 분기(`NEEDS_ESCAPE:video`)에 가둬 실제 ESC 키를
     발사했고, Kabuki가 이를 계정 선택기로 팝업시킴 → "계정 선택으로 넘어감"의 정체.
- **수정** (`TVRemoteKeyHandler.kt`):
  - 영상 판정을 시청 화면으로 게이트 (`onWatch`: URL 해시 `watch` / `#movie_player` /
    `ytlr-player-controls`·`watch-metadata`). browse 프리뷰는 조용히 pause만.
  - 루트 홈 + 포커스가 레일 밖이면 첫 번째 가시 레일 항목(`ytlr-guide-entry-renderer` →
    내부 `ytlr-button`)으로 포커스 이동 후 `HANDLED_SIDEBAR` 반환 (키 미발사).
    포커스가 이미 레일 안에 있을 때만 기존 종료 토스트 흐름.
- **실기기 검증**: 그리드 타일 → BACK → 레일 `홈` 포커스(CDP 확인).
  재생 중(`#/watch`, playing) → BACK → browse 복귀, 계정 화면 없음.
  레일 포커스 상태 → BACK → 종료 토스트 흐름 유지.

### (2) 의견 보내기 URL·QR 미반영
- **원인**: 피드백 URL 텍스트가 일반 `DIV`에 존재 (`yt-formatted-string` 아님).
  기존 DOM 스캔이 태그를 한정해 빗나감. 데이터 레이어도 배열 속 문자열을
  순회하지 않아 `texts[]`를 통과시킴. (CDP 실측으로 확정. 피드백 패널에 QR
  자체는 없음 — 일러스트만 존재.)
- **수정**:
  - `k2ReplaceTextIn(scope, from, to)` 텍스트노드 워커 추가 (태그 무관, 레이아웃 무해).
  - 도움센터: 패널 전체 순회 + 워커로 URL 교체.
  - 피드백: 가시 `ytlr-setting-action-renderer` 중 마커 포함 패널만 워커로 교체
    (+ `_k2FbPatched` 멱등, QR 스캔은 future-proof 유지).
  - `sanitizeAdsDirectly` 배열 분기에 문자열 항목 처리 추가.
  - `NativeAdSanitizer.cleanJsonObject/cleanJsonArray`에 동일 URL 규칙 추가
    (HTML 내장 페이로드 경로).
- **실기기 검증**: 의견 보내기 패널 `github.com/k2love/YT_AC/pulls` 표시
  (CDP 텍스트 + 스크린샷 `.agents/tv_screen_feedback_pulls.png`).

### (3) 좌측 패널 아래 홀드 시 쇼츠로 튐
- **원인**: `k2SetupGlobalKeyHandler`에 반복(`e.repeat`) 가드가 없어 홀드 중
  매 반복마다 포커스 점프 + `.click()`이 재발사되어 포커스가 리스트 밖으로 이탈.
- **수정**: 핸들러 진입 시 `if (e.repeat) return;` (홀드는 앱 네이티브 fast-scroll에 위임).
  Kotlin 측도 BACK/ESCAPE 반복은 조용히 소비 (JS 브리지 스팸·오종료 방지),
  나머지 키 반복은 WebView로 그대로 전달.
- **실기기 검증**: CDP 신뢰 키(`autoRepeat=true`) DOWN x14 홀드 → 포커스가
  설정 리스트 안에서 `위치`→`앱 버전`까지 정상 이동, 레일 이탈 없음.

### 부수: WebView 원격 디버깅
- `TVWebView`에 `BuildConfig.DEBUG` 게이트로 `setWebContentsDebuggingEnabled(true)`
  추가 (이번 CDP 진단에 사용, release 무영향).

---

## 2. 검증 요약
- node 하네스(실제 폴리필 평가): **28/28 통과** — 데이터 교체·DOM 스코프·멱등.
- 백 스크립트 추출물 `node --check` 통과.
- `assembleDebug` BUILD SUCCESSFUL, 루트 `YT_TV_AC.apk` 갱신·설치 후 위 항목 실기기 확인.
- 고객센터(github URL·QR) 유지 확인.

## 3. 남은 관찰 사항
- 이 TV는 logd가 앱 로그를 버리므로 이후 진단은 CDP + 스크린샷으로 수행.
- 계정 선택 화면은 비정상 재생 상태(합성 play 등) 또는 browse-ESC 경로에서만
  출현. browse-ESC 경로는 onWatch 게이트로 폐쇄됨.
