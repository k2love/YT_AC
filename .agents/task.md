# 작업 보드: 영상 시청 중 뒤로 가기 시 계정 선택 화면 이동 버그 개선

- [x] 1. 계획 수립 및 원인 분석 <!-- id: 0 -->
    - [x] 빌드 무결성 사전 확인
    - [x] 계정 선택 화면 튕김 원인(브라우저 히스토리 롤백 및 `_k2LastBrowse`) 역공학 분석
    - [x] 구현 계획서(`.agents/implementation_plan_back_key_navigation_fix_20261016.md`) 작성
- [x] 2. `h5vcc_polyfill.js` 및 `TVRemoteKeyHandler.kt` 정밀 수술 <!-- id: 1 -->
    - [x] `h5vcc_polyfill.js`: `_k2LastBrowse`의 `launch=menu` 오염 및 불필요한 URL 강제 변경 제거
    - [x] `TVRemoteKeyHandler.kt`:
      - 영상 시청 중 `history.back()`, `location.replace`, `webView.goBack()` 전면 차단
      - 영상 시청 중 네이티브 `isTrusted: true` `Escape` 키 이벤트 및 JS `Escape`/`GoBack` 디스패치로 YouTube TV 순정 Watch $\rightarrow$ Home 네비게이션 연동
      - 영상 오디오 릭 차단 (`pause()`, `muted = true`, `stopVideo()`) 유지
      - 오버레이/화질 메뉴 열림 감지 및 비디오 유지 로직 보존
- [x] 3. 빌드 검증 및 무결성 확인 <!-- id: 2 -->
    - [x] `.\gradlew.bat assembleDebug` 빌드 검증 및 `YT_TV_AC.apk` (7.38 MB) 생성 확인
    - [x] 한글 리터럴 및 인코딩 무결성 전수 확인
- [x] 4. 결과 보고 및 GitHub 동기화 <!-- id: 3 -->
    - [x] 결과 리포트(`.agents/walkthrough_back_key_navigation_fix_20261016.md`) 작성
    - [x] Git 커밋 및 원격 GitHub 푸시 완료
