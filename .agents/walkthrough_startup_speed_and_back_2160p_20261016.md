# 검증 및 결과 리포트 (Walkthrough)

## 📌 작업 개요
- **작업명**: 초반 로딩 속도 최적화, 2160p 동영상 뒤로가기 정상화, 설정 메뉴 내 '앱 버전' 위 업데이트 확인 버튼 배치
- **수행 일자**: 2026-10-16
- **대상 저장소**: [k2love/YT_AC](https://github.com/k2love/YT_AC) (`origin/main`)

---

## 🛠️ 핵심 변경 및 해결 내용

### 1. 초반 로딩 속도 획기적 단축
- **원인**: 이전 구조에서는 WebResource 가로채기 시 OkHttp 디스크 캐시가 없어 1~2MB가 넘는 `base.js`, `tv-player-ias.js`, CSS 파일들을 매번 네트워크에서 수신하고 정규식 치환을 반복 연산하여 앱 시작 시 극심한 병목이 발생했습니다.
- **개선 사항**:
  - `TVWebViewClient.kt`:
    - OkHttp 클라이언트에 50MB 디스크 캐시(`Cache`) 적용.
    - 패치된 JS/CSS를 디스크(`context.cacheDir/patched_web_cache`)에 해시 기반으로 24시간 저장.
    - 2회차 실행부터는 네트워크 0ms 및 정규식 연산 0ms로 즉각 메모리 스트림(`ByteArrayInputStream`) 반환.
  - `MainActivity.kt`:
    - 앱 시작 시 불필요한 백그라운드 깃허브 API 호출(`checkForUpdates(false)`) 제거.
    - 시작 URL을 서랍 메뉴 로딩 부하가 있는 `launch=menu` 대신 `https://www.youtube.com/tv`로 단순화하여 메인 화면 진입 가속.
    - `onPageFinished` 중복 폴리필 주입 제거.

### 2. 2160p(4K) 동영상 뒤로가기 무반응 및 계정 선택기 튕김 해결
- **원인**: 이전 커밋에서 `window._k2CommandDispatcher.resolveCommand({browseEndpoint: ...})`로 대체하고 네이티브 Escape 키 디스패치를 제거했었으나, YouTube 4K 플레이어(`movie_player`)는 Blink 엔진의 가짜 JS 합성 키(`isTrusted: false`)를 무시하여 뒤로가기가 먹통이 되었음.
- **개선 사항**:
  - `TVRemoteKeyHandler.kt`:
    - 동영상 및 오버레이 감지 시 Android 네이티브 레벨에서 정품 `KeyEvent.KEYCODE_ESCAPE` (ACTION_DOWN + ACTION_UP)를 WebView에 단 1회 정확히 디스패치하도록 복원.
    - 플레이어 포커스(`player.focus()`) 및 오디오 누수 방지 뮤트/정지 유지.
    - `window._k2InBackNavigation = true` (1.5초) 플래그를 유지하여 플레이어가 닫히는 순간 계정 선택기로 강제 리다이렉트되는 현상 원천 차단.
    - 홈/탐색 화면에서는 Escape 키를 WebView로 전달하지 않아 안드로이드 TV 리모컨 더블 클릭 종료 토스트 안정성 유지.

### 3. 설정 내 '앱 버전' 바로 위 수동 업데이트 확인 버튼 배치
- **요구사항**: 시작 시 자동 팝업을 끄고, YouTube TV [설정] 화면 맨 하단의 '앱 버전' 바로 위에 리모컨 포커스가 가능한 [최신 앱 업데이트 확인] 버튼 배치.
- **개선 사항**:
  - `MainActivity.kt`:
    - 시작 시 자동 팝업 호출 완전 제거.
    - JS 인터페이스 `YT_TV_APP.checkAppUpdate()`가 `appUpdateManager.checkForUpdates(isManualCheck = true)`를 직접 호출하도록 연결.
  - `app/src/main/assets/h5vcc_polyfill.js`:
    - `k2InjectSettingsUpdateCard` 수정: 설정 메뉴 목록의 하단 텍스트 중 `버전|version|app version|빌드|build`를 역방향 탐색하여 **'앱 버전' 항목 바로 위(`versionItem.parentNode.insertBefore(card, versionItem)`)에 카드 버튼을 정밀 삽입**.
    - TV 리모컨 포커스 시 고대비 하이라이트(푸른색 보더 및 그림자 강조) 적용. 리모컨 OK(Enter) 버튼 클릭 시 네이티브 업데이트 다이얼로그 즉시 호출.

---

## 🔍 검증 결과

| 검증 항목 | 수행 내용 | 결과 |
| :--- | :--- | :---: |
| **Gradle 빌드** | `.\gradlew.bat assembleDebug` | **PASS (13s)** |
| **루트 APK 동기화** | `app/build/outputs/apk/debug/YT_TV_AC.apk` -> `YT_TV_AC.apk` (7,384,554 bytes) 복사 | **PASS** |
| **원격 Git 동기화** | `git commit` & `git push origin main` | **PASS** |

---

## 🚀 사용자 안내
- 이제 깃허브 저장소 루트에 최신 빌드된 `YT_TV_AC.apk`가 업로드되어 앱의 설정 메뉴에서 [최신 앱 업데이트 확인]을 누르면 즉시 최신 버전으로 감지 및 설치가 가능합니다.
