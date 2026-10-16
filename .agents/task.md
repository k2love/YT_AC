# 작업 보드: 설정 화면 YouTube Premium 완전 제거 및 앱 버전 1.0.1 상향

## 1. 개요 및 사용자 요구사항
1. **[설정] 우측 메인 패널의 'YouTube Premium 가입' 완전 제거**:
   - 증상: 설정 톱니바퀴 진입 시 좌측 탭에서는 'YouTube Premium 가입' 카드가 사라졌으나, 우측 메인 패널에 커다란 YouTube Premium 가입 배너와 버튼이 그대로 노출됨.
   - 목표: 우측 메인 패널에서도 YouTube Premium 가입 안내를 완전히 소멸시키고, 첫 번째 유효 메뉴인 '구매 항목 및 멤버십'의 상세 화면이 기본으로 즉시 나타나도록 조치.
2. **[업데이트] 앱 버전 상향 및 반영**:
   - 증상: '최신 앱 업데이트 확인' 실행 시 계속 `v1.0.0`으로 표출됨.
   - 목표: `build.gradle.kts`의 버전을 `versionName = "1.0.1"`, `versionCode = 2`로 상향하여 다이얼로그에 최신 버전(v1.0.1)으로 즉시 반영.

## 2. 작업 단계
- [x] 1. 원인 정밀 규명 및 DOM 구조 분석:
  - YouTube TV의 InnerTube browse 응답에서 0번 탭(Premium)과 우측 content(`settingActionRenderer`)가 기본 매핑되어 로드됨.
  - 좌측 DOM만 숨김 처리되어 우측 `settingActionRenderer`가 초기 뷰로 그대로 렌더링됨.
- [x] 2. `implementation_plan_settings_premium_purge_and_version_bump_20261016.md` 계획서 작성
- [x] 3. 수술적 정밀 코드 수정:
  - `app/build.gradle.kts`: `versionCode = 2`, `versionName = "1.0.1"` 상향
  - `app/src/main/assets/h5vcc_polyfill.js`:
    - InnerTube API / JSON 응답 인터셉터(`sanitizeAdsDirectly`)에서 Premium 탭 및 관련 `settingActionRenderer`를 데이터 계층에서 완전히 소멸
    - `k2InjectSettingsUpdateCard()`에서 우측 패널의 프리미엄 잔여 렌더러 즉시 감지 및 제거, 설정 진입 시 첫 번째 유효 탭('구매 항목 및 멤버십')으로 자동 선택/동기화
- [x] 4. Gradle 빌드 성공 확인 (`.\gradlew.bat assembleDebug`)
- [x] 5. TV 기기(`192.168.100.121:5555`)에 APK 배포 및 설치
- [x] 6. 실제 TV 기기 화면 캡처 검증:
  - 설정 화면 진입 시 우측 메인 패널에 Premium이 사라지고 '구매 항목 및 멤버십'이 즉시 노출되는지 검증 완료 (`tv_screen_settings_verified.png`)
  - '최신 앱 업데이트 확인' 선택 시 다이얼로그에 `v1.0.1`로 정상 표시되는지 검증 완료 (`tv_screen_update_dialog_v101.png`)
- [x] 7. `walkthrough_settings_premium_purge_and_version_bump_20261016.md` 결과 리포트 작성
- [x] 8. Git 커밋 및 `origin/main` 원격 저장소 푸시
