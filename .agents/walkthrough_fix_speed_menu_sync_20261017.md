# 결과 리포트: 설정 메뉴 '동영상 속도(일반/기타 속도)' 변경 시 속도 전환 미반영 버그 정밀 해결

## 1. 개요 및 사용자 보고 현상
- **보고 현상**:
  - 리모컨 채널 핫키(`CH +` / `CH -`)로 배속(2x 등)을 조절한 후, 플레이어 HUD 설정(톱니바퀴 -> 동영상 속도) 메뉴에서 '일반(1.0x)' 또는 다른 배속을 선택하더라도 영상이 여전히 2x로 유지되고 변경되지 않는 문제 발생.
- **원인 분석**:
  1. `h5vcc_polyfill.js`의 `<video>` `ratechange` 이벤트 핸들러가 `window._k2CurrentSpeed`가 1.0이 아닐 때 `this.playbackRate = window._k2CurrentSpeed;`로 강제 재할당(Revert)하여, UI 메뉴에서 1.0x로 변경하려는 브라우저 네이티브 동작을 즉시 2.0x로 되돌려버림.
  2. YouTube TV 플레이어(`tv-player-ias.js`)의 `P.setPlaybackRate` 호출 시 UI 메뉴 클릭에서는 2번째 인자(`L`)가 전달되지 않아 `fa("yt-player-playback-rate", N)` 저장이 건너뛰어지고 우리 브릿지(`_k2CurrentSpeed`)가 1.0으로 갱신되지 못함.
  3. 신규 동영상 초기화(`iIZ`) 시 YouTube의 자체 저장소 객체(`{data: "1.5", ...}`)에 대해 `Number(object)`가 `NaN`을 반환하여 기본 1.0으로 초기화되던 취약점 존재.

---

## 2. 수술적 수정 내역

### 1) `h5vcc_polyfill.js`
- **문제의 `ratechange` 강제 Revert 리스너 완전 제거**:
  - 배속 복원 로직은 오직 새 동영상 시작 시점인 `playing` 이벤트에서만 동작하도록 분리하여, 사용자가 재생 중에 메뉴나 리모컨으로 속도를 변경할 때 어떠한 간섭도 발생하지 않도록 조치.
- **`window.k2OnSpeedChange(rate)` 브릿지 신설**:
  - YouTube 플레이어 내부에서 메뉴 클릭 등으로 배속이 변경될 때 즉시 호출되어 `window._k2CurrentSpeed = rate` 동기화, `localStorage` 저장, 우상단 `⚡ 1.0x (일반)` OSD 배지를 즉각 표시.

### 2) `TVWebViewClient.kt` (`tv-player-ias.js` 정밀 패치)
- **`P.setPlaybackRate` 브릿지 및 저장소 영구 연동**:
  - `L&&fa("yt-player-playback-rate",N)` -> `fa("yt-player-playback-rate",N),window.k2OnSpeedChange&&window.k2OnSpeedChange(N)`
  - 메뉴 선택(2번째 인자 생략) 시에도 항상 영구 저장소에 반영되고 우리 OSD 및 배속 추적 브릿지가 동기화되도록 보장.
- **신규 동영상 로드(`iIZ`) 속도 계승 로직 보정**:
  - `Number(ZD("yt-player-playback-rate"))||1` -> `(window._k2CurrentSpeed||(function(){var x=ZD("yt-player-playback-rate");return Number(x&&x.data||x);})()||1)`
  - 새 영상 시작 시 직전에 설정한 배속(1.0x, 2.0x, 3.0x 등)이 완벽하게 이어지도록 보장.

---

## 3. 실제 Android TV 기기(`192.168.100.121:5555`) 실시간 검증 결과

### 1) CDP 런타임 속도 전환 검증
```json
// 2.0배속 설정 상태에서 설정 메뉴의 '일반' 선택 직후
{
  "rateBefore": 2,
  "k2Before": 2,
  "rateImmediately": 1,
  "k2Immediately": 1
}

// 2초 후 Revert 여부 체크 (최종 상태)
{
  "finalVideoRate": 1,
  "finalK2Speed": 1
}
```
- 2x 상태에서 '일반' 선택 시 즉시 1.0배속으로 전환되며, 시간이 지나도 2x로 되돌아가지 않고 1.0x가 안정적으로 유지됨을 확인하였습니다.

### 2) 실시간 화면 캡처

| 플레이어 HUD 및 설정 진입 검증 | 1.0x (일반) 정상 전환 재생 검증 |
| :---: | :---: |
| ![Player HUD Settings](file:///C:/Users/k2love/.gemini/antigravity/brain/8dd04310-07b0-47f6-a489-f57745265845/tv_screen_menu_test_result.png) | ![1.0x Playback Verified](file:///C:/Users/k2love/.gemini/antigravity/brain/8dd04310-07b0-47f6-a489-f57745265845/tv_screen_normal_verified.png) |

---

## 4. 빌드 및 배포 상태
- Gradle 빌드: `.\gradlew.bat assembleDebug` 성공 (`BUILD SUCCESSFUL in 2s`).
- TV 설치: `adb install -r YT_TV_AC.apk` 성공.
- GitHub Push: `origin/main` 커밋 반영 완료.
