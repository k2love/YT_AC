# YouTube TV for Android Clone (YT_AC) 작업 인수인계서 (To: Muse)

## 1. 프로젝트 기본 정보
- **프로젝트 루트 경로**: `E:\AI_Projects\## YouTube TV for Android Clone`
- **GitHub 저장소**: `https://github.com/k2love/YT_AC`
- **연결된 테스트 TV 기기**: `192.168.100.121:5555` (ADB 연결 정상)
- **현재 앱 버전**: `v1.0.1` (`versionCode = 2`, `versionName = "1.0.1"`)

---

## 2. 완료된 작업 내역 (Git 및 배포 완료)
1. **GitHub Releases 등록 완료**:
   - `YT_TV_AC v1.0.1 정식 릴리즈` 태그 및 `YT_TV_AC.apk` 바이너리 첨부 등록 완료
   - 릴리즈 링크: `https://github.com/k2love/YT_AC/releases/tag/v1.0.1`
2. **설정 우측 패널 YouTube Premium 완전 제거**:
   - `app/src/main/assets/h5vcc_polyfill.js`의 `sanitizeAdsDirectly` 및 `k2InjectSettingsUpdateCard`에서 Premium 데이터/DOM 완전 필터링
   - 첫 번째 유효 메뉴인 '구매 항목 및 멤버십'으로 자동 포커스/클릭 동기화 완료
3. **설정 하단 메뉴 분리**:
   - [최신 앱 업데이트 확인]과 [앱 버전]을 독립된 2개 카드로 분리
   - [최신 앱 업데이트 확인] 클릭 시 `v1.0.1` 다이얼로그 정상 표출 확인 완료
4. **실제 TV 화면 캡처 검증 완료**:
   - 검증 캡처: `.agents/tv_screen_settings_verified.png`, `.agents/tv_screen_update_dialog_v101.png`
5. **Git 원격 푸시 완료**:
   - `origin/main` 브랜치에 최신 커밋 푸시 완료 (`commit: 39b7c5e`)

---

## 3. 다음 진행할 작업 (TODO)

### 📌 작업 명: 설정 -> 정보 -> 고객센터 깃허브 URL 및 QR 코드 변경
- **요구사항**:
  1. [설정] -> [정보] -> **[고객센터]** 선택 시 우측 메인 패널에 표시되는 URL을 `youtube.com/tv_help`에서 `github.com/k2love/YT_AC`로 변경.
  2. 중앙의 QR 코드 이미지를 `https://github.com/k2love/YT_AC`로 연결되는 QR 코드로 교체.
  3. **주의**: '의견 보내기' 메뉴는 사용자 요청에 따라 이번 작업에서 제외(건드리지 말 것).
- **관련 파일**:
  - 소스 코드: `app/src/main/assets/h5vcc_polyfill.js`
  - 생성된 QR 이미지 파일: `.agents/github_qr_test.png`
  - 생성된 QR Data URL 텍스트: `.agents/github_qr_data_url.txt`
  - 구현 계획서: `.agents/implementation_plan_settings_help_center_github_20261016.md`
  - 작업 보드: `.agents/task.md`
- **구현 힌트**:
  - 고객센터 우측 패널 컨테이너의 식별자는 `[idomkey="AboutSettingItemIdABOUT_HELP"]` 입니다.
  - 내부의 `ytlr-thumbnail-details` 요소에 `style.backgroundImage = url(...)`로 QR 코드가 지정되어 있습니다.
  - 내부의 `yt-formatted-string` 중 `youtube.com/tv_help`를 포함하는 텍스트 노드를 찾아 `github.com/k2love/YT_AC`로 교체하면 됩니다.
- **작업 후 검증**:
  - `.\gradlew.bat assembleDebug` 빌드
  - `adb install -r YT_TV_AC.apk` 배포
  - TV 화면 캡처하여 [고객센터]가 GitHub URL 및 QR 코드로 정상 표시되는지 검증
  - [의견 보내기] 등 다른 메뉴에 부작용(Side Effect)이 없는지 확인
