# 구현 계획서: 설정 > 정보 > 고객센터 깃허브 URL 및 QR 코드 등록

## 1. 개요
YouTube TV 앱 내 **[설정] -> [정보] -> [고객센터]** 선택 시 우측 메인 패널에 노출되는 기존 고객센터 안내 주소(`youtube.com/tv_help`)와 기본 YouTube QR 코드를 사용자의 공식 GitHub 저장소(`https://github.com/k2love/YT_AC` 및 `github.com/k2love/YT_AC`)로 대체 등록합니다.
*(주의: '의견 보내기' 메뉴는 사용자 요청에 따라 이번 작업에서 제외하고 다음 작업으로 이관합니다.)*

---

## 2. 변경 대상 및 수술적 수정 계획

### 1) 대상 파일
- [`app/src/main/assets/h5vcc_polyfill.js`](file:///E:/AI_Projects/##%20YouTube%20TV%20for%20Android%20Clone/app/src/main/assets/h5vcc_polyfill.js)

### 2) 수술적 최소 수정 내용
- **GitHub QR Code Data URI 상수 정의**:
  - `https://github.com/k2love/YT_AC`를 담은 고해상도 PNG base64 Data URI를 `K2_GITHUB_QR_DATA_URL` 상수로 선언.
- **고객센터(`AboutSettingItemIdABOUT_HELP`) 패널 감지 및 패치 함수**:
  - 설정 화면 주기적 점검 루프(`k2InjectSettingsUpdateCard`) 또는 MutationObserver 내에서 `AboutSettingItemIdABOUT_HELP` 컨테이너를 탐색.
  - 하위의 `ytlr-thumbnail-details` 요소의 `style.backgroundImage`를 `K2_GITHUB_QR_DATA_URL`로 교체.
  - 하위의 `yt-formatted-string` 중 `youtube.com/tv_help`를 포함하는 텍스트 노드를 찾아 `github.com/k2love/YT_AC`로 교체.
  - (선택 사항) 필요 시 제목 또는 안내 텍스트가 자연스럽게 매칭되도록 보정하되, '의견 보내기' 등 다른 설정 뷰에는 일체 영향을 미치지 않도록 `AboutSettingItemIdABOUT_HELP` 내로 스코프를 엄격히 제한.

---

## 3. 검증 계획
1. **빌드 검증**: `.\gradlew.bat assembleDebug` 빌드 오류 없음 확인.
2. **원격 배포 및 실행**: ADB를 통해 Android TV 기기(`192.168.100.121:5555`)에 설치 및 앱 실행.
3. **시각적 캡처 검증**:
   - 설정 -> 정보 -> '고객센터' 화면 진입 캡처:
     - 우측 하단 URL이 `github.com/k2love/YT_AC`로 선명하게 표시되는지 확인.
     - 중앙 QR 코드가 깃허브 QR 코드로 정상 교체 렌더링되는지 확인.
   - 설정 -> 정보 -> '의견 보내기' 화면 진입 캡처:
     - 의견 보내기 화면은 기존 형태(`youtube.com/tv/feedback`) 그대로 온전히 유지되는지 확인.
4. **산출물 이관 및 Git 푸시**: 리포트 작성 및 원격 저장소 푸시.
