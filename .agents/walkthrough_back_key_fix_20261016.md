# 작업 완료 리포트: 리모컨 뒤로가기(Back) 동작 불능 현상 원인 규명 및 근본 해결

## 1. 개요 및 사용자 요구사항
- **사용자 피드백**: "종종 뒤로가기 버튼이 안 먹어."
- **이전 증상**: "2160p 등의 영상에서 뒤로가기 버튼이 동작하지 않음."

---

## 2. 근본 원인 분석 결과 (Root Cause Analysis)

### 원인 1: `document.body`가 '팝업/오버레이'로 100% 오인됨
- YouTube TV 웹앱의 모든 페이지 `<body>` 태그에는 기본 클래스로 `app-quality-root`가 포함되어 있습니다.
- `TVRemoteKeyHandler.kt`의 백스택 스크립트에서 포커스 조상을 거슬러 올라가며 검사하는 정규식:
  ```javascript
  if (/(menu|dialog|popup|panel|sheet|settings|quality|options|listbox)/i.test(hn) && !/(control-bar|player-control|progress)/i.test(hn))
  ```
  `hn`에 `app-quality-root`의 `quality`가 매칭되어 `document.body`가 팝업/메뉴(`found`)로 오판되었습니다.
- `BODY` 내에서 `[aria-label*="뒤로"]`를 탐색하는 과정에서, 비디오 탐색바(Seek bar)의 **`"0초 뒤로 건너뜁니다..."`** 버튼을 닫기 버튼으로 착각하여 클릭(`closer.click()`)하거나, `NEEDS_ESCAPE:menu`만 발생시켰습니다.
- **결과**: 사용자가 영상 시청 중 나가려고 뒤로가기를 눌렀으나, 실제로는 **재생바의 0초 되감기가 클릭**되거나 영상이 닫히지 않고 먹통이 되었습니다.

### 원인 2: 서브 페이지(설정, 검색, 채널 등)가 `ROOT_HOME`으로 오인됨
- 영상 재생이나 팝업이 아닌 상태는 무조건 `return 'ROOT_HOME';`으로 처리되어 WebView에 아무런 키 이벤트도 전달하지 않고 "뒤로 가기 버튼을 한 번 더 누르면 종료됩니다" 토스트만 띄웠습니다.
- **결과**: 설정, 검색, 채널 등 하위 화면에서 뒤로가기를 눌러도 이전 화면으로 돌아가지 않았습니다.

---

## 3. 적용된 수술적 정밀 수정 (Surgical Fix)
- 대상 파일: [`app/src/main/java/com/k2/youtubetv/remote/TVRemoteKeyHandler.kt`](file:///E:/AI_Projects/##%20YouTube%20TV%20for%20Android%20Clone/app/src/main/java/com/k2/youtubetv/remote/TVRemoteKeyHandler.kt)

1. **오버레이 탐색 대상에서 `BODY` 및 `HTML` 완벽 배제**:
   - `k2Visible(el)`에서 `el === document.body || el === document.documentElement || el.tagName === 'BODY' || el.tagName === 'HTML'`는 즉시 `false` 반환.
   - 포커스 조상 탐색 `while` 루프에서 `node === document.body || node.tagName === 'BODY'` 도달 시 즉시 탐색 중단(`break`).
   - 제외 키워드에 `app-quality-root`를 명시하여 오탐 완전 방지.

2. **닫기(`closer`) 버튼 탐색 정밀화**:
   - `[aria-label]` 검사 시 `"건너뜁니다"`, `"초 뒤"`, `"seek"`, `"scrub"`, `"시작하려면"` 등이 포함된 탐색바 요소는 철저히 제외.
   - 실제 닫기/취소/뒤로 버튼만 클릭하도록 정밀 매칭.

3. **서브 페이지 vs 루트 홈 정확한 분기**:
   - `window.location.hash`를 분석하여 `#/`, `""`, `#/home`, `#/browse` 등 루트 홈일 때만 `ROOT_HOME` 처리.
   - 그 외의 하위 페이지(`#/settings`, `#/browse?c=...`, `#/channel/...` 등)에서는 `NEEDS_ESCAPE:subpage`를 전달하여 YouTube TV 내부 히스토리를 통해 이전 화면으로 자연스럽게 복귀.

4. **영상 시청 중 동작 개선**:
   - 플레이어 컨트롤(HUD)이 열려 있을 때는 HUD만 닫히도록 분기 (`NEEDS_ESCAPE:hud`).
   - 전체화면 영상 재생 중에는 비디오를 음소거/정지하고 안전하게 이전 화면으로 복귀 (`NEEDS_ESCAPE:video`).

---

## 4. 실제 TV 기기(`192.168.100.121:5555`) 검증 결과

1. **영상 시청 중 뒤로가기 버튼 1회 입력**:
   - [tv_screen_playing.png](file:///E:/AI_Projects/##%20YouTube%20TV%20for%20Android%20Clone/tv_screen_playing.png) (영상 재생 중)
   - [tv_screen_after_back.png](file:///E:/AI_Projects/##%20YouTube%20TV%20for%20Android%20Clone/tv_screen_after_back.png) (뒤로가기 1회 후 홈 화면 정상 복귀 확인)
2. **서브 페이지(라이브 카테고리)에서 뒤로가기 입력**:
   - 라이브 콘텐츠 그리드 -> 사이드바 -> 홈 화면 순으로 완벽 복귀 확인.
3. **루트 홈 화면에서 뒤로가기 2회 연속 입력**:
   - 1회 입력 시 안내 토스트 표출, 2초 내 2회 입력 시 Android TV 홈 런처로 정상 종료 확인.

---

## 5. 결론
종종 뒤로가기가 먹히지 않았던 근본 원인(BODY의 `app-quality-root` 오탐으로 인한 시크바 오클릭 및 서브페이지 미지원)을 완전히 해결하였으며, 실제 TV 기기 검증 및 Git 원격 저장소 배포까지 완료했습니다.
