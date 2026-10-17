# 작업 보드: YouTube TV 순정 플레이어 HUD 비주얼 완전 복원 및 UI 밀림 방지

## 목표
1. 상단 영상 제목 및 컨트롤 툴팁 문자 설명(채널, 이전, 다음, 좋아요, 싫어요, 댓글, 질문하기, 저장, Super Thanks, 자막, 설정)의 검은 박스 완전 제거 및 투명 배경 복원
2. 간헐적으로 전체 UI가 TV 상단 밖으로 200px 이상 밀려 올라가는 현상 원천 차단

---

## 작업 단계

### 1차: HUD 및 툴팁 문자 설명 투명화
- [x] 계획서 작성 (`.agents/implementation_plan_pure_hud_transparency_20261017.md`)
- [x] 소스 코드 수술적 정밀 수정 (`h5vcc_polyfill.js`, `TVWebViewClient.kt` PATCH_VERSION 7)
- [x] 릴리즈 v1.0.3 빌드 및 실기 설치
- [x] 결과 리포트 작성 (`.agents/walkthrough_pure_hud_transparency_20261017.md`)

### 2차: UI 상단 200px 밀림(Shift) 현상 원천 차단
- [x] 원인 분석 및 계획서 작성 (`.agents/implementation_plan_prevent_ui_shift_20261017.md`)
  - Android WebView 네이티브 스크롤 오프셋 발생 차단 (`scrollTo(0,0)`, `overScrollMode = NEVER`)
  - Window SoftInput 패닝 차단 (`android:windowSoftInputMode="adjustNothing|stateAlwaysHidden"`)
  - DOM/클래스 리플로우 유발 요소 정리 (`purgeQualityRoot` 및 `qualityObserver` 제거)
  - `PATCH_VERSION = 8` 상향
- [x] 소스 코드 수술적 정밀 수정 (`TVWebView.kt`, `AndroidManifest.xml`, `h5vcc_polyfill.js`, `TVWebViewClient.kt`)
- [x] 릴리즈 빌드 (`.\gradlew.bat assembleRelease` 성공)
- [x] 실기 TV 설치 및 단일 스크린샷 검증 (`verified_ui_pos.png`)
- [x] 결과 리포트 작성 (`.agents/walkthrough_prevent_ui_shift_20261017.md`)
