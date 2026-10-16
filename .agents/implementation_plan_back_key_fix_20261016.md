# 구현 계획서: 리모컨 뒤로가기(Back) 동작 불능 현상 원인 규명 및 근본 해결

## 1. 개요
사용자 피드백:
- "종종 뒤로가기 버튼이 안 먹어."
- 이전 이슈: "2160p 등의 영상에서 뒤로가기 버튼이 동작하지 않음."

## 2. 근본 원인 분석 (Root Causes)

### 원인 1: `document.body`가 '오버레이 팝업'으로 오인됨
- YouTube TV의 `<body>` 태그에는 기본 클래스로 `app-quality-root`가 포함되어 있음.
- `TVRemoteKeyHandler.kt`의 백스택 스크립트에서 포커스 조상을 탐색하는 루프:
  ```javascript
  if (/(menu|dialog|popup|panel|sheet|settings|quality|options|listbox)/i.test(hn) && !/(control-bar|player-control|progress)/i.test(hn)) { found = node; foundVia = 'focus-ancestor'; break; }
  ```
  `hn`에 `app-quality-root`의 `quality`가 매칭되어 `document.body`가 `found`(오버레이 메뉴)로 지정됨.
- `found.querySelector('[aria-label*="뒤로"]...')` 탐색 시 재생 바의 `"0초 뒤로 건너뜁니다..."` 버튼을 닫기 버튼(`closer`)으로 오인하여 클릭함.
- 결과: 사용자가 뒤로가기를 누르면 영상 시크바의 0초 되감기가 클릭되거나 `NEEDS_ESCAPE:menu`가 전달되어 영상에서 빠져나가지 못하고 먹통이 됨.

### 원인 2: 서브 페이지(설정, 검색, 채널 등)가 `ROOT_HOME`으로 처리됨
- 비디오 재생 중이 아니면 무조건 `return 'ROOT_HOME';`으로 처리되어 웹뷰에 아무런 키 이벤트도 전달되지 않음.
- 이로 인해 사용자가 [설정], [검색], [채널], [재생목록] 등의 서브 화면에 있을 때 뒤로가기를 누르면 화면이 뒤로 가지 않고 "뒤로 가기 버튼을 한 번 더 누르면 종료됩니다." 토스트만 뜸.

## 3. 정밀 해결 방안 (Surgical Fix)

### A. `TVRemoteKeyHandler.kt`의 `handleBackAction` 정밀 개편
1. **`BODY` 및 `HTML` 오버레이 배제**:
   - `k2Visible(el)`에서 `el === document.body || el === document.documentElement || el.tagName === 'BODY' || el.tagName === 'HTML'`는 즉시 `false` 반환.
   - 포커스 조상 탐색 `while` 루프에서 `node === document.body || node.tagName === 'BODY'` 도달 시 탐색 중단(`break`).

2. **닫기(`closer`) 버튼 탐색 정밀화**:
   - `[aria-label*="뒤로"]` 검사 시 `"건너뜁니다"`, `"초 뒤"`, `"seek"`, `"scrub"`, `"시작하려면"` 등이 포함된 시크바 요소는 철저히 제외.
   - `found`가 `BODY`나 `HTML`인 경우 닫기 버튼 탐색을 수행하지 않음.

3. **서브 페이지 vs 루트 홈 정확한 분기**:
   - `hash` 및 `href` 검사:
     - 루트 홈: `hash === '' || hash === '#/' || hash === '#/home' || hash === '#/browse'`
     - 서브 페이지: `#/settings`, `#/search`, `#/channel/...`, `#/playlist...` 등
   - 서브 페이지 상태일 때는 `NEEDS_ESCAPE:subpage` 또는 `HISTORY_BACK`을 반환하여 이전 화면으로 정상 복귀할 수 있도록 `KEYCODE_ESCAPE`를 웹뷰에 디스패치.
   - 진짜 루트 홈 화면에 있을 때만 `ROOT_HOME`으로 반환하여 2회 연속 입력 시 앱 종료 토스트 동작.

4. **영상 시청 중(`isVideoActive`) 처리 개선**:
   - 플레이어 컨트롤(컨트롤 바, 팝업 등)이 열려 있을 때는 `NEEDS_ESCAPE:controls`로 컨트롤 바만 닫기 (영상 정지 X).
   - 순수 영상 재생 중일 때는 영상을 정지/음소거하고 `NEEDS_ESCAPE:video`로 재생 화면 이탈.

## 4. 검증 계획
1. `gradlew assembleDebug` 빌드 검증
2. TV 기기(`192.168.100.121:5555`)에 설치 및 앱 실행
3. 시나리오별 리모컨 뒤로가기 테스트:
   - 영상 시청 중 리모컨 [뒤로가기] -> 영상 종료 후 홈/이전 화면 정상 복귀 확인
   - 설정 화면(`#/settings`)에서 [뒤로가기] -> 홈 화면 정상 복귀 확인
   - 검색 화면(`#/search`)에서 [뒤로가기] -> 홈 화면 정상 복귀 확인
   - 홈 화면(`#/`)에서 [뒤로가기] 1회 -> 토스트 확인, 2회 -> 앱 정상 종료 확인
