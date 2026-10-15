# YouTube TV for Android Clone (YT_TV_AC)

[![Android](https://img.shields.io/badge/Platform-Android%20TV%20%7C%20Google%20TV-3DDC84?logo=android&logoColor=white)](https://www.android.com/tv/)
[![Kotlin](https://img.shields.io/badge/Kotlin-1.9.22-7F52FF?logo=kotlin&logoColor=white)](https://kotlinlang.org/)
[![Cobalt](https://img.shields.io/badge/Cobalt-24.lts-FF0000?logo=youtube&logoColor=white)](https://cobalt.dev/)
[![Ad-Free](https://img.shields.io/badge/Ad--Free-100%25%20Zero--Ad-brightgreen)]()
[![4K / 8K](https://img.shields.io/badge/Resolution-4K%20%2F%208K%20Unlocked-blue)]()

> **YouTube for Android TV (v7.28.300)** 순정 앱과 100% 동일한 사용자 경험을 제공하면서, 광고를 원천 박멸하고 4K/8K 고화질 및 완전 투명 UI를 탑재한 독립형 오픈소스 Android TV 애플리케이션입니다.

---

## 🌟 주요 특징 (Key Features)

### 1. 🛡️ 100% 제로-애드 (Zero-Ad Architecture)
- **홈 화면/인피드 광고 차단**: 대문 머스트헤드 배너, 추천 피드 내 스폰서 영상 카드를 네트워크 및 DOM 레벨에서 완전 삭제.
- **영상 재생 광고 원천 봉쇄**: 영상 시작 전(프리로) 및 시청 중(미드롤) 1~2초 후 튀어나오는 모든 강제 광고를 `JSON.parse` 딥 필터링과 `204 No Content` 네트워크 차단으로 박멸.
- **백그라운드 광고음 누출 방지**: 영상 전환 또는 뒤로가기 시 잔류 광고 오디오가 재생되는 현상을 네이티브 킬스위치로 100% 차단.

### 2. 🎬 4K (2160p) & 8K (4320p) 고화질 원천 언락
- **720p 다운그레이드 캡 무력화**: 저사양 TV 인식으로 인해 유튜브 플레이어가 720p로 화질을 제한하던 필터 체인(`B3`, `k2`, `w$n`)을 서지컬 패치하여 무력화.
- **화질 선택 메뉴 전수 해금**: 비디오 옵션 메뉴에서 **1080p FHD, 1440p QHD, 2160p 4K, 4320p 8K**를 직접 선택 가능.
- **VP9 & AV1 코덱 지원**: `MediaSource` 코덱 쿼리를 개방하여 고효율 4K/8K 스트림 원활 재생.

### 3. ✨ 순정 완전 투명 UI (True Transparent UI)
- **부팅 로고 투명화**: 오리지널 웹의 불투명 회색 배경(`RGB(40,40,40)`)을 제거하고 알파 투명 PNG로 원천 치환.
- **컨트롤 및 메뉴 시커먼 박스 제거**: Android TV WebView GPU 컴포지터에서 불투명 검은 상자로 렌더링되던 Kabuki 프레임워크의 그라디언트 스크림을 `none`으로 중화하여, 영상 시청 중 컨트롤 바와 자막, 메뉴가 완전 투명하게 오버레이됨.
- **텍스트 가독성 그림자**: 투명 배경에서도 제목과 재생 시간을 또렷하게 볼 수 있도록 부드러운 `text-shadow` 적용.

### 4. 🎮 스마트 TV 리모컨 완벽 호환
- D-Pad 십자키, 선택(Enter), 미디어 제어키(재생/일시정지/탐색) 네이티브 매핑.
- **화질/설정 메뉴 뒤로가기 지능형 처리**: 화질 선택 팝업이나 메뉴가 열려 있을 때는 영상을 멈추지 않고 메뉴만 닫으며, 영상 시청 화면에서 나갈 때에만 오디오를 끄고 뒤로 이동.

---

## 🏗️ 아키텍처 구조 (Architecture)

```
[ Android TV Remote / OS ]
           │
           ▼
┌────────────────────────────────────────────────────────┐
│  MainActivity (Immersive Sticky Fullscreen)            │
│  └─ TVRemoteKeyHandler (Menu-Aware Back Navigation)    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  TVWebView (Cobalt Platform UA & Hardware Compositor)  │
│  ├─ CobaltJsBridge (Starboard C++ Service Emulation)   │
│  ├─ TVWebChromeClient (Transparent Video Poster)       │
│  └─ TVWebViewClient                                    │
│       ├─ Ad Tracker / Stream Interceptor (204 Drop)    │
│       ├─ tv-player-ias.js Patcher (4K/8K Unlock)       │
│       ├─ kabuki.css Neutralizer (Pure Transparent UI)  │
│       └─ NativeAdSanitizer (HTML/JSON Deep Clean)      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  h5vcc_polyfill.js (Runtime Browser Environment)       │
│  ├─ JSON.parse Hook (Zero-Ad Payload Annihilator)      │
│  ├─ 4K Display Metrics (3840x2160, DPR 2.0)            │
│  └─ InstantAdKiller (50ms Zero-Frame Guard)            │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 빌드 및 설치 방법 (Build & Installation)

### 사전 요구사항
- JDK 17 이상
- Android SDK (API Level 34, minSdk 26)

### 빌드 (Build)
```bash
# 프로젝트 디렉토리로 이동
cd "## YouTube TV for Android Clone"

# 디버그 APK 빌드
.\gradlew.bat assembleDebug
```
빌드가 완료되면 아래 경로에 패키징된 APK가 생성됩니다:
`app/build/outputs/apk/debug/YT_TV_AC.apk` (약 6.38 MB)

### 설치 (Install via ADB)
Android TV 기기의 개발자 옵션에서 **네트워크 디버깅** 또는 **USB 디버깅**을 활성화한 후:
```bash
# 기기 연결 (네트워크 디버깅 시)
adb connect <기기_IP_주소>:5555

# APK 설치
adb install -r app/build/outputs/apk/debug/YT_TV_AC.apk
```

---

## 📂 프로젝트 디렉토리 구조 (Directory Structure)

```
## YouTube TV for Android Clone/
├── .agents/                    # 리버스 엔지니어링 분석 스크립트 및 인수인계 문서
├── app/
│   ├── src/main/
│   │   ├── assets/
│   │   │   ├── h5vcc_polyfill.js          # Starboard H5VCC 브릿지 & 런타임 제로-애드 엔진
│   │   │   └── transparent_logo_b64.txt   # 알파 투명 순정 로고 Data URI
│   │   ├── java/com/k2/youtubetv/
│   │   │   ├── MainActivity.kt            # 메인 진입점 및 리모컨 제어 라우터
│   │   │   ├── auth/                      # 구글 계정 동기화 모듈
│   │   │   ├── bridge/                    # Starboard 플랫폼 서비스 라우터
│   │   │   ├── remote/
│   │   │   │   └── TVRemoteKeyHandler.kt  # 스마트 TV 리모컨 핸들러 (팝업 감지)
│   │   │   └── webview/
│   │   │       ├── TVWebView.kt           # TV 특화 WebView
│   │   │       ├── TVWebViewClient.kt     # 네이티브 광고 차단 & 4K/8K 언락 인터셉터
│   │   │       ├── TVWebChromeClient.kt   # 비디오 포스터 투명화
│   │   │       └── NativeAdSanitizer.kt   # HTML/JSON 실시간 살균기
│   │   └── res/                           # 안드로이드 TV 배너 및 리소스
│   └── build.gradle.kts                   # 앱 빌드 스크립트 (YT_TV_AC.apk 출력)
├── gradle/                                # Gradle Wrapper
├── build.gradle.kts                       # 루트 빌드 스크립트
├── settings.gradle.kts                    # 프로젝트 설정
└── README.md                              # 프로젝트 문서
```

---

## 📜 면책 조항 (Disclaimer)
본 프로젝트는 순수 연구 및 학습 목적의 리버스 엔지니어링(Clean-room Reverse Engineering) 프로젝트입니다. YouTube 및 Google TV는 Google LLC의 등록 상표입니다.
