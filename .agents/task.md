# 작업 보드: 설정 > 고객센터 깃허브 URL 및 QR코드 변경

## 1. 개요 및 사용자 요구사항
- **요구사항**: 설정 -> 정보 -> '고객센터' 화면의 웹 주소와 QR 코드를 우리 깃허브(`https://github.com/k2love/YT_AC`)로 등록.
- **제외 사항**: '의견 보내기'는 이번 작업에서 건드리지 않고 다음 작업으로 이관.
- **성공 기준**:
  - '고객센터' 선택 시 우측에 표시되는 URL 텍스트가 `youtube.com/tv_help`에서 `github.com/k2love/YT_AC`로 변경됨.
  - 우측에 표시되는 QR 코드가 `https://github.com/k2love/YT_AC`로 연결되는 정상 QR 코드로 대체 렌더링됨.
  - '의견 보내기' 등 다른 설정 화면 및 기능에는 일체 영향이 없음.
  - 실제 Android TV 기기(`192.168.100.121`)에서 캡처 검증 완료.

## 2. 작업 단계
- [/] 1. '고객센터' 우측 뷰의 DOM 및 렌더러 구조 정밀 분석
- [/] 2. `implementation_plan_settings_help_center_github_20261016.md` 계획서 작성
- [/] 3. 깃허브 URL용 QR 코드 생성 (SVG 또는 Data URI / Canvas / img)
- [/] 4. `app/src/main/assets/h5vcc_polyfill.js`에 수술적 정밀 최소 수정 적용:
  - '고객센터' 패널 감지 시 텍스트 및 QR 코드를 깃허브 저장소 정보로 교체
- [/] 5. Gradle 빌드 성공 확인 (`.\gradlew.bat assembleDebug`)
- [/] 6. TV 기기(`192.168.100.121:5555`)에 APK 배포 및 설치
- [/] 7. 실제 TV 기기 화면 캡처 검증:
  - 설정 -> 정보 -> 고객센터 선택 시 깃허브 주소 및 QR 코드 정상 표시 확인
  - 의견 보내기 및 타 메뉴 정상 동작 확인
- [/] 8. `walkthrough_settings_help_center_github_20261016.md` 결과 리포트 작성
- [ ] 9. Git 커밋 및 `origin/main` 푸시
