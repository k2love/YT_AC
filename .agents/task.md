# 작업 보드: 뒤로가기 시 계정 선택 화면 전환 원천 차단 및 안정적 뒤로가기 시스템 구축

- [x] 1. 문제 분석 및 계획 수립 <!-- id: 0 -->
    - [x] YouTube TV(Kabuki) 라우터 `_.n.Fg` 및 `requestAccountSelectorCommand` 역공학 분석
    - [x] `TVRemoteKeyHandler.kt`의 다중 키 머신건 발사 및 홈 화면 Escape 발사 결함 식별
    - [x] 구현 계획서(`.agents/implementation_plan_back_navigation_account_fix_20261016.md`) 작성
- [x] 2. `TVWebViewClient.kt`에 라우터 가드 및 커맨드 디스패처 패치 적용 <!-- id: 1 -->
    - [x] `_.n.Fg`의 `ACCOUNT_EVENT_TRIGGER_CAST_PROTECTION` 조건 무력화
    - [x] `_.kk`에서 `window._k2CommandDispatcher` 노출
    - [x] `resolveCommand`에서 뒤로가기 시 계정 선택 명령을 홈(`default`) 명령으로 자동 전환
- [x] 3. `h5vcc_polyfill.js` 및 `TVRemoteKeyHandler.kt` 수술적 개편 <!-- id: 2 -->
    - [x] `h5vcc_polyfill.js`에 `_k2InBackNavigation` 및 `_k2HasLoadedHome` 플래그 관리 추가
    - [x] `TVRemoteKeyHandler.kt`에서 키 난사 제거 및 단일 이벤트 / 커맨드 디스패치 방식으로 전환
    - [x] 홈 화면에서 WebView로 Escape 전달 차단 (계정 선택 팝업 방지)
    - [x] `ACTION_UP` 소비 및 `MainActivity.kt`의 `onBackPressed` 연동
- [x] 4. 빌드 검증 및 깃허브 배포 <!-- id: 3 -->
    - [x] `.\gradlew.bat assembleDebug` 빌드 검증
    - [x] 루트 `YT_TV_AC.apk` 갱신 및 Git 커밋/푸시
    - [x] 결과 보고서(`.agents/walkthrough_back_navigation_account_fix_20261016.md`) 작성
