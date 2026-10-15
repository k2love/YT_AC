# YouTube for Android TV 역공학 사양서 (Part 2: 계정 인증, URL 생성 및 CobaltService 프로토콜)

본 문서는 YouTube for Android TV (v7.28.300)의 계정 인증 연동(GMS Auth), 실행 시 URL 및 파라미터 조합 규칙, 그리고 핵심 브릿지 계층인 `CobaltService` IPC 통신 규격을 원본 바이너리 의존성 없이 클린룸(Clean-room) 방식으로 재구현할 수 있도록 정리한 정밀 기술 명세서입니다.

---

## 1. 개요 및 하이브리드 아키텍처 연동 구조

YouTube for Android TV는 순수 네이티브 앱이 아닌, **Android 네이티브 호스트 셸**과 Google의 맞춤형 C++ 웹 런타임인 **Cobalt 엔진(`libchrobalt.so`)**, 그리고 웹앱 프론트엔드인 **Kabuki(`https://www.youtube.com/tv`)**가 결합된 3계층 하이브리드 아키텍처입니다.

```
+-------------------------------------------------------------------+
|               Kabuki Frontend (HTML5 / WebGL WebApp)             |
|                   https://www.youtube.com/tv                      |
+---------------------------------+---------------------------------+
                                  |
               Starboard / CobaltService Bridge (JSON IPC)
                                  |
+---------------------------------v---------------------------------+
|            Cobalt C++ Engine (libchrobalt.so / Starboard)         |
+---------------------------------+---------------------------------+
                                  | JNI
+---------------------------------v---------------------------------+
|         Android Host App (MainActivity / StarboardBridge)          |
|    - GMS Core Auth (GoogleAuthUtil / AccountManager)              |
|    - Play Integrity (PoTokensClient / DroidGuard)                 |
|    - Google TV Channel Recommendations                            |
+-------------------------------------------------------------------+
```

---

## 2. 앱 실행 시 URL 생성 및 파라미터 주입 메커니즘

### 2.1 진입점 및 URL 결정 흐름
- **메서드 오프셋**: `MainActivity.getIntentUrlAsString()` (`0x28F33C`) & `MainActivity.getArgs()` (`0x28F55C`)
- **기본 URL 획득**: `AndroidManifest.xml`의 `<meta-data android:name="cobalt.APP_URL" android:value="https://www.youtube.com/tv"/>` 로드

### 2.2 인텐트(Intent) 분석 및 쿼리 파라미터 조합 규칙
1. **딥링크(Deep Link) 처리**:
   - `intent.getData() != null`인 경우 `dbp.bu()`를 호출하여 URI 파싱.
   - 내부 안드로이드 런처 플래그 제거: `force_fullscreen`, `finish_on_ended`, `forceKids`
   - 스킴(`https://`), 호스트(`www.youtube.com`), 경로(`/tv`) 검증 후 비디오 ID/토픽 전달.
   - `gtv_kids_profile=true` 여부에 따라 추가 플래그 설정.
2. **콜드 부팅(Cold Boot) 시 진입 경로 플래그**:
   - **리모컨 전용 버튼 실행**: 인텐트 `extras` 내 `remote_button` 불리언 값이 `true`인 경우:
     - 쿼리 파라미터: `launch=remote` 추가
     - 로그: `"Received intent sent from YouTube remote button"`
   - **Android TV / Leanback 런처 실행**: 인텐트 액션이 `android.intent.action.MAIN`이고 카테고리가 `android.intent.category.LAUNCHER` 또는 `android.intent.category.LEANBACK_LAUNCHER`인 경우:
     - 쿼리 파라미터: `launch=menu` 추가
3. **최종 URL 포맷**:
   - 일반 메뉴 실행 시: `https://www.youtube.com/tv?launch=menu`
   - 리모컨 핫키 실행 시: `https://www.youtube.com/tv?launch=remote`
   - 추가 `url_params` 검증 정규식: `^[a-zA-Z0-9_=]*$`

### 2.3 Cobalt 엔진 CLI 플래그 주입
`MainActivity.getArgs()`는 Cobalt 프로세스 초기화 시 아래 인자들을 구성하여 전달합니다:
```bash
--url=https://www.youtube.com/tv?launch=menu
```
동시에 `MainActivity.getJavaSwitches()`를 통해 다음 하드웨어 최적화 스위치를 Map 형태로 엔진에 전달:
- `DisableGpuRasterizationMsaa`
- `V8InitialOldSpaceSize`
- `EnableAsyncDnsAndDoH`
- `AreaBasedVideoBufferBudget`
- `CobaltDynamicMojoPipeSubresourceSize`
- `EnableCobaltAudioCaptureFastTrack`
- `Force720pUiOn1GbDevices`

---

## 3. 핵심 통신 계층: 12개 CobaltService 상세 명세

`MainActivity.createStarboardBridge()`(`0x28F27C`)는 12개의 Cobalt 플랫폼 서비스를 Starboard 브릿지에 등록합니다. 각 서비스는 고유한 네임스페이스와 JSON 기반의 양방향 IPC 메시징을 처리합니다.

| 서비스 식별자 (Service Name) | 구현 클래스 | 역할 및 책임 |
| :--- | :--- | :--- |
| `com.google.youtube.tv.syncauthcredential` | `Lgey;` (`Lgez;`) | 계정 토큰 및 인증 상태 양방향 동기화 |
| `com.google.youtube.tv.recommendations` | `Lges;` (`Lgen;`) | Android TV 홈 화면 채널 및 추천 피드 연동 |
| `com.google.android.gms.potokens` | `Lged;` (`Lgdv;`) | Play Integrity PO 토큰 (InnerTube 봇 차단 우회 증명) |
| `com.google.android.gms.droidguard` | `Lgds;` (`Lgdz;`) | 기기 하드웨어 무결성 증명 (DroidGuard) |
| `com.google.youtube.tv.syncvisitor` | `Lgfe;` (`Lgdz;`) | 게스트 및 방문자 식별자(`visitorData`) 동기화 |
| `com.google.youtube.tv.syncdeviceid` | `Lgfc;` (`Lgdz;`) | TV 고유 디바이스 ID 동기화 |
| `com.google.youtube.tv.syncrollouttoken` | `Lgfd;` (`Lgdv;`) | 기능 A/B 테스팅 및 롤아웃 토큰 동기화 |
| `com.google.android.gms.cast.tv` | `Lgdk;` / `Lgdr;` | 모바일-TV 화면 공유(Cast MDx) 수신 |
| `com.google.youtube.tv.networkmonitor` | `Lgdu;` (`Lgdv;`) | 실시간 대역폭 및 네트워크 연결 모니터링 |
| `com.google.android.tv.playbillinglr` | `Lgea;` (`Lgdz;`) | 영화/채널 멤버십 인앱 결제(Play Billing) |
| `com.google.android.youtube.tv.prodlogger`| `Lgee;` (`Lgef;`) | 프로덕션 크래시 및 텔레메트리 로깅 |

---

## 4. `com.google.youtube.tv.syncauthcredential` 정밀 프로토콜

YouTube TV의 진정한 추천 알고리즘과 개인화 피드가 작동하는 핵심 심장부입니다.

### 4.1 Kabuki(웹앱) -> Native: 인증 정보 동기화 (`SyncAuthCredential`)
사용자가 웹 화면에서 로그인(QR 코드, tv.youtube.com/activate, 또는 기기 연동)을 완료하면, Kabuki 웹앱이 네이티브로 다음 JSON 메시지를 전송합니다:

```json
{
  "action": "SyncAuthCredential",
  "message": {
    "accessToken": "ya29.a0AfH6SM...",
    "expiry": 1729050000000,
    "ownerAccountEmail": "user@gmail.com",
    "activeVisitorData": "Cgt2S1BNQ0hWdWlsNCi...",
    "dataSyncId": "104928394829104",
    "reportAuthCredentialIntervalSeconds": 1800,
    "gaiaAuthenticatedIdentityType": "GAIA_USER",
    "pageId": null
  }
}
```

- **필드 정의**:
  - `accessToken`: Google OAuth2 / InnerTube API 호출용 베어러 토큰.
  - `expiry`: 토큰 만료 시점 (Unix Epoch Milliseconds).
  - `ownerAccountEmail`: 현재 활성 구글 계정 이메일.
  - `activeVisitorData`: InnerTube 전용 세션 추적 문자열 (홈 추천 알고리즘 컨텍스트의 핵심).
  - `dataSyncId`: 기기 간 이어보기 및 기록 동기화 ID.
  - `reportAuthCredentialIntervalSeconds`: 네이티브 측 갱신 보고 주기 (기본값: 1800초 / 30분).

### 4.2 Native -> Kabuki(웹앱): 인증 정보 보고 (`ReportAuthCredential`)
앱이 시작되거나 백그라운드에서 복귀(`beforeStartOrResume`), 또는 토큰 갱신 주기가 도래했을 때 네이티브가 검증을 거쳐 웹앱으로 토큰을 밀어 넣습니다:

```json
{
  "action": "ReportAuthCredential",
  "message": {
    "accessToken": "ya29.a0AfH6SM...",
    "expiry": 1729050000000,
    "ownerAccountEmail": "user@gmail.com"
  }
}
```

- **토큰 유효성 검사 로직** (`Lgew;->()` `0x3D8788`):
  ```java
  boolean isValid = !TextUtils.isEmpty(accessToken) && 
                    (Instant.now().toEpochMilli() < expiry);
  ```

---

## 5. `com.google.youtube.tv.recommendations` 추천 연동 규격

오리지널 앱이 안드로이드 TV 런처의 '맞춤 채널(Channels)' 및 '다음 볼만한 동영상(Watch Next)'에 추천 목록을 등록하는 인터페이스입니다:

- **지원 셸프(Shelves)**:
  - `CONTINUE_WATCHING` (시청 중인 콘텐츠 이어보기)
  - `SHORTS` (유튜브 쇼츠 전용 채널)
- **주요 파라미터**:
  - `shelfParam`: InnerTube 셸프 식별자
  - `topic`: 추천 주제 카테고리
  - `accountProfile` / `accountId` / `profileId`: 프로필 다중 계정 식별자
- **명령 체계**:
  - `recommend`: 추천 영상 메타데이터 리스트 수신 및 Android TV Provider DB 삽입
  - `getPartnerId`: 파트너 ID 응답

---

## 6. 클린룸(Clean-room) 복제 구현 지침

우리가 직접 구현할 자체 YouTube for Android TV 앱에서 원본과 100% 동일한 추천 및 UI를 달성하기 위한 구조 설계:

1. **웹 컨테이너 선택**:
   - 가벼운 웹 렌더러(Webkit/Blink 기반 웹뷰 또는 커스텀 크로미움)를 탑재.
2. **진입 URL**:
   - `https://www.youtube.com/tv?launch=menu`로 접속.
3. **자바스크립트 브릿지 주입 (`window.h5vcc` 및 CobaltService)**:
   - 웹앱이 로드될 때 `window.h5vcc` 및 Starboard 메시지 버스를 모방하는 자바스크립트 인터페이스 제공.
   - `SyncAuthCredential` 액션을 수신하여 토큰/세션을 저장하고, `ReportAuthCredential`을 발행하여 로그인 세션을 완벽 유지.
   - GMS의 `GoogleAuthUtil` 스코프(`oauth2:https://www.googleapis.com/auth/youtube`)로 기기 내 구글 계정 토큰을 자동 획득하여 무마찰 로그인 제공.
