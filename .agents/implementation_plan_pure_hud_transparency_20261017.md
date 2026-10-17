# 구현 계획서: 순정 플레이어 HUD 및 컨트롤 라벨 완전 투명화

## 1. 개요 및 배경
- **문제 정의**:
  - 동영상 재생 중 리모컨 아래 방향(DOWN) 버튼을 눌러 플레이어 HUD를 표시하고 좌우로 이동할 때, 컨트롤 버튼마다 동적으로 나타나는 문자 설명(툴팁 라벨)에 불투명한 짙은 회색/검은색 박스 배경이 렌더링되는 문제.
  - 대상 라벨: 채널, 이전, 다음, 좋아요(숫자 표기 포함), 싫어요(숫자 표기 포함), 댓글, 질문하기, 저장, Super Thanks, 자막, 설정
- **근본 원인**:
  1. 유튜브 TV 웹앱(`kabuki_main.js`)은 버튼 포커스 시 `<div class="TamOWc"><yt-formatted-string class="A71IFd">`를 동적 생성하며, 기본 CSS에 `.A71IFd { background-color: rgb(55, 55, 55); }`가 정의되어 있음.
  2. 안드로이드 TV WebView 환경에서 저사양 모드(`app-quality-root`)가 활성화될 경우 `.app-quality-root .ApXCd .QOsyFf .E7WdFf { background-color: rgb(0, 0, 0); border-radius: 2.5rem; }` 및 `.KQT3Oe`, `.CO0KFd`, `.dsDLs`, `.pPJooc` 등이 검은색 배경을 강제함.
  3. `TVWebViewClient`의 정적 에셋 디스크 캐싱(24시간)으로 인해 `PATCH_VERSION` 상향 없이 CSS만 수정할 경우 실기에 반영되지 않음.

---

## 2. 수술적 수정 명세

### A. `app/src/main/assets/h5vcc_polyfill.js`
1. **마스터 CSS 주입 (`getMasterCss()`)**:
   - `.A71IFd, .TamOWc, .TamOWc .A71IFd, [class*="A71IFd"], [class*="TamOWc"], .E7WdFf, .QOsyFf, .ApXCd, .KQT3Oe, .CO0KFd, .dsDLs, .pPJooc` 선택자에 대해 완전 투명화 및 순백색 폰트 강제:
     ```css
     background: transparent !important;
     background-color: transparent !important;
     background-image: none !important;
     box-shadow: none !important;
     border: none !important;
     color: #ffffff !important;
     text-shadow: 0 1px 4px rgba(0, 0, 0, 0.9), 0 0 2px rgba(0, 0, 0, 0.9) !important;
     ```
2. **저사양 모드 실시간 박멸 (`purgeQualityRoot()`)**:
   - `documentElement` 및 `body`에서 `app-quality-root` 클래스를 즉각 제거하는 함수 구현.
   - `MutationObserver`(`subtree: true`)로 동적 재부여 시 즉시 제거.

### B. `app/src/main/java/com/k2/youtubetv/webview/TVWebViewClient.kt`
1. `PATCH_VERSION`: 5 $\rightarrow$ 7 상향하여 이전 디스크 캐시 완전 무효화.
2. `appendRules`에 동일한 툴팁 및 컨트롤 투명화 CSS 규칙 추가.

---

## 3. 검증 계획
1. `.\gradlew.bat assembleRelease` 빌드 성공 확인.
2. `adb install -r YT_TV_AC.apk` 실기 설치.
3. 영상 재생 상태에서 리모컨 DOWN 1회 입력 후 좌우 포커스 이동 시 모든 버튼 라벨의 배경 투명화 및 텍스트 렌더링 확인.
