# 작업 보드: 설정 메뉴 업데이트/버전 탭 분리 및 YouTube Premium 가입 항목 숨김

## 1. 개요 및 사용자 요구사항
- **요구사항 1**: YouTube TV [설정] 메뉴 맨 아래에 있는 `최신 앱 업데이트 확인`과 `앱 버전` 두 메뉴가 리모컨 선택 시 동시에 선택(하이라이트)되는 문제를 완벽히 분리.
- **요구사항 2**: [설정] 메뉴 최상단에 있는 `YouTube Premium 가입` 항목 완전 숨김/제거.

## 2. 작업 목록
- [x] 1. WebView DOM 구조 및 CSS 클래스 정밀 분석 (설정 화면 진입 후 탭 상태 검사)
- [x] 2. `implementation_plan_settings_menu_split_and_premium_hide_20261016.md` 계획서 작성
- [x] 3. `h5vcc_polyfill.js` 수술적 정밀 수정:
  - `YouTube Premium 가입` 탭 숨김 처리 (CSS + JS 감시 및 첫 탭 자동 전환)
  - `최신 앱 업데이트 확인` 탭과 `앱 버전` 탭의 독립성 보장:
    - 복제 시 선택/포커스 클래스 및 `aria-selected` 초기화 (`k2SetElementFocusState`)
    - 포커스 진입/이탈(`focusin`/`focusout`) 시 `versionTab`과 상호 간섭 차단
    - 우측 패널 연동 분리 (`k2UpdateRightDetailPanel`)
    - D-Pad 전역 키 인터셉터 (`k2SetupGlobalKeyHandler`) 구현으로 완벽한 상하 이동 및 엔터 다이얼로그 호출 보장
- [x] 4. APK 빌드 (`gradlew assembleDebug`)
- [x] 5. TV 기기(`192.168.100.121:5555`)에 APK 설치 및 앱 실행
- [x] 6. TV 화면 캡처 및 리모컨 이동 테스트로 완벽 검증:
  - 설정 최상단 `YouTube Premium 가입` 메뉴 완전 제거 및 첫 탭 `구매 항목 및 멤버십` 노출 확인 (`tv_screen_membership_active.png`)
  - `최신 앱 업데이트 확인` 선택 시 단독 하이라이트 확인 (`tv_screen_update_focused.png`)
  - `앱 버전` 선택 시 단독 하이라이트 확인 (`tv_screen_version_focused.png`)
  - OK(Enter) 클릭 시 안드로이드 네이티브 최신 버전 업데이트 다이얼로그 즉시 팝업 확인 (`tv_screen_dialog_enter.png`)
- [ ] 7. GitHub 원격 저장소 커밋 및 푸시
- [ ] 8. `walkthrough_settings_menu_split_and_premium_hide_20261016.md` 작성 및 사용자 보고
