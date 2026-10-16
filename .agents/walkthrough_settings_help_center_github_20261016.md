# 작업 리포트: 설정 > 정보 > 고객센터 깃허브 URL 및 QR 코드 교체

> **작업 일시**: 2026-10-16
> **대상**: `https://github.com/k2love/YT_AC` (v1.0.1, `versionCode=2`)
> **검증 기기**: Android TV `192.168.100.121:5555` (실기기 캡처 검증 완료)

---

## 1. 요구사항 및 결과

| 요구사항 | 결과 |
| :--- | :--- |
| 고객센터 우측 패널 URL을 `youtube.com/tv_help` → `github.com/k2love/YT_AC`로 변경 | ✅ 실기기 캡처에서 `github.com/k2love/YT_AC` 표시 확인 |
| 중앙 QR 코드를 `https://github.com/k2love/YT_AC` 연결 QR로 교체 | ✅ 캡처 QR 디코딩 결과 `https://github.com/k2love/YT_AC` 완전 일치 (OpenCV 검증) |
| '의견 보내기' 메뉴는 건드리지 않음 | ✅ `youtube.com/tv/feedback` 그대로 유지 캡처 확인 |

---

## 2. 변경 내용 (수술적 최소 수정)

### 대상 파일
- `app/src/main/assets/h5vcc_polyfill.js` (+4.8 KB: 상수 1개, 함수 1개, 인터벌 1개)

### 추가 요소
1. **`K2_GITHUB_QR_DATA_URL` 상수**: `https://github.com/k2love/YT_AC`를 담은 2809바이트 PNG의 Base64 Data URI (3770자, 단일 행). 원본: `.agents/github_qr_data_url.txt` (생성 스크립트: `.agents/generate_qr.py`, ECC-H).
2. **`k2PatchHelpCenterPanel()` 함수** (1초 간격 실행):
   - `[idomkey="AboutSettingItemIdABOUT_HELP"]` 컨테이너로 스코프를 엄격히 제한.
   - 하위 `ytlr-thumbnail-details`의 `backgroundImage`(인라인 우선, 없으면 computed)를 GitHub QR Data URI로 교체 (`!important`, 기존 사이즈·레이아웃 스타일 유지).
   - 하위 `yt-formatted-string` 중 `youtube.com/tv_help` 포함 텍스트만 `github.com/k2love/YT_AC`로 교체.
   - 이미 패치된 상태면 스킵하므로 반복 실행이 안전(idempotent). 로그 1회만 출력.
3. **`setInterval(k2PatchHelpCenterPanel, 1000)`**: 기존 설정 루프 옆에 등록. idom 리렌더에도 자동 재적용.

### 스코프 안전성
- 선택자가 고객센터 패널 내부로 한정되므로 '의견 보내기'(`youtube.com/tv/feedback`)를 포함한 다른 모든 설정 화면에 영향 없음. 실기기에서 의견 보내기 화면 원형 유지 확인.

---

## 3. 검증 기록

1. **빌드**: `.\gradlew.bat assembleDebug` → BUILD SUCCESSFUL. 산출물 `app/build/outputs/apk/debug/YT_TV_AC.apk` (6.17 MB)를 루트 `YT_TV_AC.apk`로 복사.
2. **배포**: `adb install -r YT_TV_AC.apk` → Success. 앱 실행 후 설정 진입.
3. **캡처 검증** (`.agents/tv_screen_help_center_github.png`, 1920x1080):
   - 우측 패널 하단 URL `github.com/k2love/YT_AC` 선명 표시.
   - 중앙 QR을 OpenCV `QRCodeDetector`로 디코딩 → `https://github.com/k2love/YT_AC` 완전 일치.
   - 의견 보내기 화면 `youtube.com/tv/feedback` 원형 유지.
4. **부수 확인**: OTA 업데이트 다이얼로그(`v1.0.1` 감지)가 정상 동작 중이며 뒤로가기로 닫힘. Premium 잔재 없음.

---

## 4. 다음 작업 이관
- '의견 보내기' 메뉴 교체는 사용자 요청에 따라 미착수(다음 작업으로 이관).
- 관련 분석 자료: `.agents/help_center_dom.json`, `.agents/help_center_renderer.json` (렌더러 구조: `qrBg`/`qrStyle` + `texts[3]`).
