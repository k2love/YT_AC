# 구현 계획서 - YouTube for Android TV 클린룸 복제 앱 (YouTube TV Native Clone)

## 1. 개요 및 배경
- **목적**: 원본 YouTube for Android TV (v7.28.300)의 이질감 없는 순정 UI/UX 및 100% 동일한 개인화 영상 추천 알고리즘을 복제하는 클린룸(Clean-room) 안드로이드 TV 애플리케이션 개발.
- **기존 솔루션(SmartTube)의 한계 극복**:
  - SmartTube는 안드로이드 Leanback UI 컴포넌트로 화면을 별도 조립하여 폰트, 애니메이션, 포커스 전환 등에서 원본과 심한 이질감이 존재함.
  - 모바일/비공식 API 크롤링으로 인해 실제 사용자의 고유 시청 기록 기반 추천 알고리즘이 온전하게 반영되지 않음.
- **해결 방안**:
  - 원본 TV 프론트엔드(`https://www.youtube.com/tv?launch=menu`)를 그대로 수용하고, 역공학으로 밝혀낸 `window.h5vcc` 시스템 모듈과 `CobaltService` IPC 계층을 네이티브 코드로 완벽하게 에뮬레이션함.

---

## 2. 제안 아키텍처 및 구현 사양

### 2.1 주요 기술 스택
- **타깃 플랫폼**: Android TV / Google TV (API 레벨 26+ ~ 34)
- **언어 및 툴체인**: Kotlin 1.9+, AndroidX, Coroutines
- **렌더링 엔진**: Android System WebView (하드웨어 가속 Blink/Chromium 코어)
- **미디어 엔진**: Chromium 내장 MSE (Media Source Extensions) + Widevine CDM 하드웨어 디코더

### 2.2 핵심 구현 모듈
```
app/src/main/
├── java/com/clone/youtubetv/
│   ├── MainActivity.kt                # 진입점, 풀스크린 몰입 모드, 인텐트 파싱
│   ├── bridge/
│   │   ├── CobaltJsBridge.kt          # @JavascriptInterface 구현 (JavaScript-Kotlin 통신)
│   │   ├── PlatformServiceRouter.kt   # 12개 CobaltService 메시지 라우터
│   │   └── services/
│   │       ├── SyncAuthCredentialService.kt # 계정 인증 동기화 (ReportAuthCredential)
│   │       ├── RecommendationsService.kt    # Android TV 채널 연동
│   │       ├── PoTokensService.kt           # Play Integrity PO 토큰 스텁/생성
│   │       └── NetworkMonitorService.kt     # 대역폭 모니터링
│   ├── webview/
│   │   ├── TVWebView.kt               # D-Pad 포커스, 4K 하드웨어 가속 설정
│   │   ├── TVWebChromeClient.kt       # 미디어 권한, 콘솔 디버깅
│   │   └── TVWebViewClient.kt         # h5vcc 폴리필 스크립트 주입
│   └── auth/
│       └── GoogleAuthManager.kt       # AccountManager / Google Play Services 연동
└── assets/
    └── h5vcc_polyfill.js              # window.h5vcc 완전한 스펙 주입 스크립트
```

---

## 3. 단계별 세부 작업 및 검증 계획 (Milestones)

### [1단계] 셸 뷰 및 웹앱 환경 구성 (Target: 순정 UI 구동)
1. Android TV용 단일 액티비티 템플릿 구성 (`leanback` 테마 비활성화, 순수 풀스크린 액티비티).
2. `TVWebView` 구성:
   - User-Agent를 Cobalt 24 / Starboard 16 형식으로 위장.
   - WebGL 2.0, DOM Storage, MSE, EME 활성화.
3. `assets/h5vcc_polyfill.js` 생성 및 `onPageStarted` 시점에 주입.
4. **검증**: `https://www.youtube.com/tv?launch=menu` 로드 시 데스크톱/모바일 리다이렉트 없이 원본 TV UI가 100% 동일한 픽셀 단위로 표시되는지 확인.

### [2단계] TV 리모컨 D-Pad 포커스 및 미디어 재생 최적화
1. 리모컨 방향키(D-Pad Up/Down/Left/Right/Select/Back) 키 이벤트를 WebView 내부 DOM 포커스로 무지연 전달.
2. 4K/60fps VP9/AV1 재생 시 프레임 드롭 없는 하드웨어 비디오 오버레이 동작 확인.
3. **검증**: 리모컨으로 메뉴 탐색, 영상 클릭, 전체화면 재생, 뒤로가기가 순정 YouTube TV와 동일한 감도로 작동하는지 확인.

### [3단계] `SyncAuthCredential` 계정 인증 연동 (Target: 100% 순정 추천 알고리즘)
1. `SyncAuthCredentialService` 구현:
   - 기기 내 구글 계정 토큰 자동 추출 또는 화면 내 웹 로그인 지원.
   - `ReportAuthCredential` 메시지를 웹앱으로 발행하여 자동 로그인 유지.
   - 웹앱이 생성한 `activeVisitorData`, `dataSyncId`를 안전한 로컬 저장소에 보존.
2. **검증**: 로그인 후 홈 화면에 사용자의 실제 구독 채널, 시청 기록, 오리지널 맞춤 추천 영상이 1:1로 일치하게 노출되는지 확인.

### [4단계] Android TV 런처 추천 채널(`Recommendations`) 연동
1. `RecommendationsService` 구현:
   - `CONTINUE_WATCHING` 및 `SHORTS` 셸프 데이터를 받아 `TvContractCompat`에 등록.
2. **검증**: 안드로이드 TV 메인 홈 화면에 'YouTube 맞춤 동영상' 및 '이어보기' 채널 행이 정상 생성되는지 확인.

---

## 4. 리스크 관리 및 대응 방안
- **Widevine L1/L3 DRM 문제**: 4K 유료 콘텐츠의 경우 하드웨어 L1이 필요할 수 있으나, 일반 유튜브 4K/8K 60fps는 VP9/AV1 무암호화 스트림이므로 표준 WebView MSE로 100% 재생 가능.
- **Google InnerTube PO Token 정책 변화**: 필요 시 WebView 컨텍스트에서 자체 발급되는 PO Token과 네이티브 `PoTokensService` 간의 동기화 구조 유지.
