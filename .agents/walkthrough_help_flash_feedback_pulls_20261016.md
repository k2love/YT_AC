# 작업 리포트: 고객센터 원본 플래시 제거 + 의견 보내기 pulls 교체

> **작업 일시**: 2026-10-16 (후속)
> **제약**: adb 미사용 — node 하네스 실행 검증 + 빌드 검증만 수행, 실기기 확인은 사용자 측에 이관

---

## 1. 요구사항 및 대응

| 요구사항 | 대응 |
| :--- | :--- |
| 기존 QR·URL이 약 1초간 보였다가 교체됨 (플래시) | 데이터 레이어 선교체로 원본이 렌더링 전에 제거됨. DOM 패치는 폴백으로만 유지 |
| '의견 보내기' → `https://github.com/k2love/YT_AC/pulls` | URL 텍스트 + pulls 전용 QR로 교체 (도움말·타 메뉴 무영향) |
| adb로 조정하지 말 것 | 설치·캡처 없이 코드 작업 + 하네스/빌드 검증만 수행 |

---

## 2. 변경 내용 (`app/src/main/assets/h5vcc_polyfill.js`)

### (1) 데이터 레이어 선교체 — `sanitizeAdsDirectly` 객체·배열 분기 (플래시 원천 제거)
- 직접 문자열 속성: `youtube.com/tv_help` → `github.com/k2love/YT_AC`,
  `youtube.com/tv/feedback` → `github.com/k2love/YT_AC/pulls`.
- 배열 분기 신규 처리: 기존에는 배열 속 문자열을 순회하지 않아 렌더러 `texts[]`
  안의 URL이 그대로 통과했음. 문자열 항목도 동일 규칙으로 교체.
- QR 아트워크: 길이 2000자 초과 `data:image…;base64,…` 값에 한해, 같은 객체의
  형제 값에 `tv_help`가 있으면 도움말 QR로, `tv/feedback`이 있으면 pulls QR로
  이미지 바이트만 교체 (`url("…")`·`background-image:` 래퍼 보존).
  이미 교체된 값은 원본 마커가 없어져 1회성으로 종료. 길이 가드로 작은 아이콘 보호.

### (2) `k2PatchFeedbackPanel()` 신규 (DOM 폴백)
- `youtube.com/tv/feedback` 포함 `yt-formatted-string`을 찾아 pulls URL로 교체 후,
  해당 텍스트의 `closest('[idomkey]')` 스코프 안에서만 `ytlr-thumbnail-details`
  배경을 pulls QR로 교체. 도움센터·타 패널에 영향 없음.

### (3) 즉시형 DOM 폴백 — 문서 레벨 MutationObserver
- 요소 삽입 시점에 마이크로태스크로 두 패널 패치 실행 (페인팅 전, 1초 대기 없음).
- 삽입 게이트 + 300ms 스로틀로 재생 중 오버헤드 제한. 기존 1초 인터벌은 백스톱 유지.

### (4) pulls QR 리소스
- `.agents/github_qr_pulls.png` (3060 B) + `.agents/github_qr_pulls_data_url.txt` (4102자).
- 도움말 QR과 동일 조건(ECC-H, box 12, border 3)으로 생성, OpenCV 디코딩
  `https://github.com/k2love/YT_AC/pulls` 완전 일치 확인.

---

## 3. 검증 (adb 없이)
- **node 하네스** (`C:\Users\k2love\AppData\Local\Temp\opencode\test_panels.js`):
  실제 폴리필을 스텁 브라우저 전역으로 평가 후 후크된 `JSON.parse`·캡처된
  인터벌 콜백을 구동. **23/23 통과**:
  - 도움말/의견 데이터 객체의 URL·QR 교체 및 래퍼 보존, 마커 없는 data URI untouched,
  - 광고·화질 살균 회귀 없음, DOM 스코프 분리 및 멱등성.
- 하네스 과정에서 실제 버그 1건 발견·수정: 배열 속 문자열 미순회 (위 (1) 반영).
- **빌드**: `.\gradlew.bat assembleDebug` BUILD SUCCESSFUL. 루트 `YT_TV_AC.apk`
  갱신(6.17 MB) 후 APK 내 `assets/h5vcc_polyfill.js`에 신규 코드 포함 확인.

## 4. 사용자 측 확인 요청
1. 앱 설치 후 설정 → 정보 → **고객센터**: 원본(`youtube.com/tv_help`, 기존 QR)이
   한 프레임도 보이지 않고 곧바로 GitHub URL·QR로 표시되는지.
2. **의견 보내기**: URL이 `github.com/k2love/YT_AC/pulls`, QR이 pulls QR인지
   (휴대폰으로 스캔 시 pulls 페이지로 이동하는지).
3. 타 메뉴 이상 없음.
