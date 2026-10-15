# 작업 보드: 설정 메뉴 연동 및 앱 업데이트 수동 확인 시스템 구현

- [x] 1. 계획 수립 및 GitHub 릴리즈 상태 분석 <!-- id: 0 -->
    - [x] GitHub API 404 원인 규명 (최초 릴리즈 미발행 상태 확인)
    - [x] 설정 화면 연동 및 리모컨 단축키 연동 설계
    - [x] 구현 계획서(`.agents/implementation_plan_settings_update_menu_20261016.md`) 작성
- [x] 2. `AppUpdateManager.kt` 고도화 (설정 및 피드백 다이얼로그) <!-- id: 1 -->
    - [x] `showSettingsDialog()` 구현: 현재 버전, 기능 상태, [업데이트 확인] 버튼이 포함된 TV 스타일 설정 창
    - [x] 404(릴리즈 미등록), 최신 버전 유지, 신규 버전 발견, 네트워크 오류 등 상황별 맞춤 AlertDialog 피드백 제공
- [x] 3. 네이티브 및 리모컨 키 연동 <!-- id: 2 -->
    - [x] `MainActivity.kt`: `YT_TV_APP` JavascriptInterface 브릿지 추가 (`checkAppUpdate()`, `openSettings()`)
    - [x] `TVRemoteKeyHandler.kt`: `KEYCODE_MENU`, `KEYCODE_SETTINGS` 입력 시 설정/업데이트 창 호출
- [x] 4. YouTube TV 웹 설정 화면 내 업데이트 카드 주입 <!-- id: 3 -->
    - [x] `h5vcc_polyfill.js`: 설정 화면 진입 시 'YT_TV_AC 앱 정보 및 업데이트' 위젯 주입 및 클릭/포커스 이벤트 연동
- [x] 5. 빌드 검증 및 릴리즈 연동 <!-- id: 4 -->
    - [x] `.\gradlew.bat assembleDebug` 빌드 검증 및 `YT_TV_AC.apk` (7.38 MB) 생성 확인
    - [x] 결과 리포트(`.agents/walkthrough_settings_update_menu_20261016.md`) 작성
    - [x] Git 커밋 및 원격 GitHub 푸시 완료
