# YouTube for Android TV (v7.28.300) 오리지널 역공학 분석 리포트 (Part 1)

## 1. 개요
* **분석 대상 파일**: `YouTube+for+Android+TV_7.28.300_APKPure.xapk`
* **아키텍처**: ARM 32-bit (`armeabi-v7a`)
* **핵심 바이너리**:
  * `com.google.android.youtube.tv.apk` (Java/Kotlin 앱 껍데기 및 GMS 연동)
  * `libchrobalt.so` (58.01 MB, Google Cobalt C++ TV 웹 브라우저 & 렌더링 코어)
* **분석 도구**: IDA Pro 9.4 (Hex-Rays Decompiler) + REA MCP + 커스텀 정적 분석기

---

## 2. 오리지널 유튜브 TV 앱의 실제 구동 아키텍처

```
[ Android OS / Leanback Launcher ]
           ↓
[ 1. Java 진입 액티비티 ]
   - com.google.android.apps.youtube.tv.activity.MainActivity
   - com.google.android.apps.youtube.tv.activity.ShellActivity
   - 메타데이터 로드: cobalt.APP_URL = "https://www.youtube.com/tv"
           ↓ (GMS 계정 토큰 및 시스템 파라미터 획득)
[ 2. 네이티브 C++ 코어: libchrobalt.so (Cobalt) ]
   - Starboard 플랫폼 추상화 레이어 초기화
   - H5VCC (HTML5 Video Content Container) Mojom IPC 인터페이스 등록
   - 독자적 User-Agent 헤더 생성
           ↓ (웹 렌더링)
[ 3. 구글 공식 웹앱 (https://www.youtube.com/tv) 실행 ]
   - InnerTube API (https://youtubei.googleapis.com) 통신
   - 내 구글 계정 100% 동기화 추천 알고리즘 피드 수신
```

---

## 3. 핵심 발견 및 추출 데이터

### 3.1 공식 진입점 URL
* **메인 웹앱 진입 URL**: `https://www.youtube.com/tv`
* **계정/권한 엔드포인트**: `https://youtube.com/tv/uma`
* **스트리밍 청크 서버**: `https://googlevideo.com/`, `https://c.youtube.com/`

### 3.2 진짜 추천 알고리즘의 심장: InnerTube API & OAuth 스코프
오리지널 앱이 내 계정의 시청 기록과 취향에 100% 일치하는 맞춤형 추천 피드를 가져올 때 사용하는 통신 규격:
* **API 엔드포인트**: `https://youtubei.googleapis.com`
* **요구되는 구글 OAuth 2.0 스코프**:
  * `https://www.googleapis.com/auth/youtube`
  * `https://www.googleapis.com/auth/youtube.force-ssl`
  * `https://www.googleapis.com/auth/identity.lateimpersonation`

### 3.3 전설적인 구글 TV 네이티브 브리지: `H5VCC` 인터페이스
`libchrobalt.so` 분석 결과, 웹앱(`youtube.com/tv`)이 TV 하드웨어 및 구글 인증을 제어하기 위해 호출하는 핵심 내부 Mojom 객체군이 식별되었습니다:
* **`h5vcc_system.mojom.H5vccSystem`**: TV 모델명, 칩셋, 고유 디바이스 ID 제공 (구글 서버가 "정품 TV"로 승인하는 핵심 지점)
* **`h5vcc_storage.mojom.H5vccStorage`**: 영구 로그인 세션 및 쿠키 보존
* **`h5vcc_settings.mojom.H5vccSettings`**: 4K/HDR 해상도 및 오디오 코덱 설정
* **`h5vcc_runtime.mojom.H5vccRuntime`**: 웹앱 생명주기 및 리로드 제어

### 3.4 User-Agent 포맷 규격
* 템플릿: `Mozilla/5.0 (%s) AppleWebKit/537.36 (KHTML, like Gecko) %s Safari/537.36`
* 첫 번째 `%s`: 디바이스/OS 정보 (예: `Linux; GoogleTV`)
* 두 번째 `%s`: Cobalt 엔진 버전 및 디바이스 식별 문자열 (예: `Cobalt/24.lts...`)
