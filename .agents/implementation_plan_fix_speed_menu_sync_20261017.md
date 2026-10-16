# 구현 계획서: 설정 메뉴 '동영상 속도(일반/기타 속도)' 변경 시 속도 전환 미반영 버그 정밀 수정

## 1. 문제 원인 정밀 분석
- **현상**:
  - 리모컨 채널 핫키로 배속을 조절(예: 2.0x, 3.0x 등)한 후, 설정 메뉴(톱니바퀴 -> 동영상 속도)에서 '일반(1.0x)' 또는 다른 속도를 선택해도 2.0x에서 변경되지 않고 강제 유지되는 현상 발생.
- **근본 원인**:
  1. `h5vcc_polyfill.js` 내 `<video>` 요소의 `ratechange` 이벤트 핸들러가 `window._k2CurrentSpeed`가 1.0이 아닐 때 `this.playbackRate = window._k2CurrentSpeed;`를 강제로 재할당하고 있었음.
  2. 사용자가 설정 메뉴에서 '일반'을 클릭하면 YouTube 내부 플레이어가 `<video>.playbackRate = 1.0`을 설정하지만, 즉시 발생한 `ratechange` 이벤트에 의해 `window._k2CurrentSpeed`(2.0)로 다시 덮어써져 버림.
  3. 또한 YouTube TV 플레이어(`tv-player-ias.js`)의 `P.setPlaybackRate` 메서드 호출 시, 메뉴를 통한 클릭에서는 2번째 인자(`L`)가 전달되지 않아 `fa("yt-player-playback-rate", N)`가 호출되지 않고 persistent 저장소에 미반영됨.
  4. 플레이어 초기화(`iIZ`) 함수에서도 `ZD("yt-player-playback-rate")`가 반환하는 객체(`{data: "1.5", ...}`)에 대해 `Number(object)`가 `NaN`을 반환하여 기본값 1로 폴백되는 구조적 결함이 있었음.

---

## 2. 수술적 수정 계획

### A. `h5vcc_polyfill.js`
1. **문제의 `ratechange` 강제 덮어쓰기 로직 제거**:
   - `ratechange` 이벤트 리스너 제거.
   - 재생 속도 복원은 새 동영상 시작 시점인 `playing` 이벤트(`this.playbackRate !== window._k2CurrentSpeed`)에서만 안전하게 동작하도록 격리.
2. **`window.k2OnSpeedChange(rate)` 브릿지 함수 신설**:
   - 플레이어 엔진 또는 메뉴에서 배속 변경 시 즉시 `window._k2CurrentSpeed = rate` 동기화.
   - `localStorage` 저장 및 우상단 OSD 배지(`⚡ 1.0x (일반)` 등) 정상 호출.

### B. `TVWebViewClient.kt` (`tv-player-ias.js` 정밀 패치)
1. **`P.setPlaybackRate`에 브릿지 및 영구 저장 연동**:
   - `L&&fa("yt-player-playback-rate",N)` -> `fa("yt-player-playback-rate",N),window.k2OnSpeedChange&&window.k2OnSpeedChange(N)`
   - 메뉴 클릭(2번째 인자 부재) 시에도 항상 YouTube 내부 저장소 저장 및 `k2OnSpeedChange` 호출 보장.
2. **신규 동영상 초기화(`iIZ`) 속도 복원 보정**:
   - `Number(ZD("yt-player-playback-rate"))||1` -> `(window._k2CurrentSpeed||(function(){var x=ZD("yt-player-playback-rate");return Number(x&&x.data||x);})()||1)`
   - 새 동영상 로드 시 사용자가 설정한 배속을 완벽하게 계승.

---

## 3. 검증 계획
1. Gradle 빌드 성공 검증 (`.\gradlew.bat assembleDebug`).
2. TV 기기(`192.168.100.121:5555`) APK 재배포 및 설치.
3. 리모컨 핫키로 2x (또는 3x) 설정 후, HUD 설정(톱니바퀴) -> 동영상 속도 -> '일반' 선택 시 실제 재생 속도가 1.0배속으로 정상 전환되는지 CDP 및 화면 검증.
4. '일반' 선택 시 우상단에 `⚡ 1.0x (일반)` OSD 배지 노출 확인.
5. 다음 영상 전환 시 설정한 배속 유지 여부 검증.
6. 결과 리포트 작성 및 Git 커밋/푸시.
