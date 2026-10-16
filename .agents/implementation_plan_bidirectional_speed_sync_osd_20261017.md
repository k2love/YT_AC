# 작업 계획서: 메뉴 속도 전환과 리모컨 속도 조절 간의 완벽한 양방향 동기화 및 OSD 배지 보장

## 1. 개요 및 배경
- **현상 분석**:
  1. 사용자가 2.0x 상태에서 플레이어 HUD 설정(톱니바퀴 -> 동영상 속도) 메뉴를 열어 '일반(1.0x)'으로 변경했을 때 화면 우측 상단에 `⚡ 1.0x (일반)` OSD 배지가 표시되지 않음.
  2. 그 직후 리모컨 `CH +` 버튼을 누르면 1.0x 기준 다음 단계인 1.25x가 아니라 이전 속도(2.0x)의 다음 단계인 2.25x로 올라감.
- **원인 규명**:
  - 기존 코드에서 롤백 버그를 방지하기 위해 `<video>` 요소의 `ratechange` 이벤트 핸들러를 제거했었음.
  - 이로 인해 YouTube TV 메뉴(웹 UI)에서 재생속도를 변경할 경우 `window._k2CurrentSpeed` 전역 변수가 갱신되지 않고 2.0x로 남아 있었으며, OSD 배지 트리거도 발생하지 않음.
  - 따라서 리모컨 핫키(`CH +` / `CH -`) 입력 시 이전 값(2.0)을 기준으로 계산되어 불일치 현상이 발생함.

---

## 2. 해결 전략 (Surgical Patch)

1. **내부 변경 가드 플래그(`window._k2InternalRateChange`) 도입**:
   - 리모컨 핫키(`k2SetPlaybackRate`) 실행 시 `_k2InternalRateChange = true`를 설정하여 중복 호출 및 무한 루프를 원천 방지.
2. **`<video>` `ratechange` 이벤트 핸들러 복원 및 정밀 동기화**:
   - 웹 UI(설정 메뉴)에서 비디오의 `playbackRate`가 변경될 때(`!window._k2InternalRateChange && Math.abs(_k2CurrentSpeed - r) > 0.01`):
     - `window._k2CurrentSpeed = r` 즉각 동기화.
     - `localStorage`에 영구 저장(`yt-player-playback-rate`).
     - `k2ProtectAgainstStall(this)` 호출로 비디오 멎음 방지.
     - `showSpeedOsd(r)` 호출로 우측 상단에 `⚡ 1.0x (일반)` 또는 해당 배속 배지 표출.
3. **기존 플레이어 래퍼(`player.setPlaybackRate`, `k2OnSpeedChange`) 안전화**:
   - `!window._k2InternalRateChange` 조건으로 감싸 이중 배지 표시 및 불필요한 중복 실행 방지.

---

## 3. 검증 계획
1. `.\gradlew.bat assembleDebug` 빌드 확인.
2. `adb install -r YT_TV_AC.apk`로 Android TV 실기기에 배포.
3. 2.0x 상태에서 메뉴로 1.0x(일반) 전환 시:
   - CDP를 통해 `window._k2CurrentSpeed`와 `video.playbackRate`가 즉시 1로 변경되는지 검증.
   - 우측 상단 `⚡ 1.0x (일반)` 배지가 정상 렌더링되는지 스크린샷 캡처.
4. 직후 리모컨 `CH +` 조작 시:
   - 2.25x가 아닌 정확히 1.25x(`⚡ 1.25x 속도`)로 변경되는지 CDP 및 화면 캡처 검증.
