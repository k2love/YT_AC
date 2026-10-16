# 구현 계획서: YouTube TV 재생 속도 제한 완전 해제 (최대 4배속 및 3배속 지원, UI 메뉴 확장 및 리모컨 연동)

## 1. 개요 및 목적
- **목적**:
  - YouTube TV 플레이어에서 기본 2.0배속으로 제한되어 있는 재생 속도를 사용자 요구에 따라 **최대 4배속(2.25x, 2.5x, 2.75x, 3.0x, 3.5x, 4.0x)**까지 완전 해제.
  - 플레이어 설정의 "동영상 속도" 서브메뉴에 2.25배속부터 4.0배속까지 옵션을 추가하여 리모컨 DPAD로 선택 가능하게 구성.
  - TV 리모컨의 채널 상/하, 페이지 상/하, 컬러 버튼을 통해 즉시 속도를 조절할 수 있는 핫키 기능 및 우상단 속도 OSD 배지 제공.
  - 다음 영상 재생 시에도 설정한 재생 속도가 유지되도록 보장.

## 2. 역공학 분석 결과
1. **플레이어 내부 상한선 (`tv-player-ias.js`)**:
   - `this.nM = 2;` 및 `granularVariableSpeedConfig.maximumPlaybackRate = 200`으로 인해 `this.nM`이 2로 고정.
   - `P.getAvailablePlaybackRates`: `WsS.filter(g => g >= L && g <= v)`에서 `v = this.nM = 2`로 인해 2.0 초과분이 잘려나감 (`WsS`에는 이미 `[2.5, 3, 3.5, 4]`가 포함되어 있음).
   - `AU1(player, rate)`: `v = player.getAvailablePlaybackRates()`의 마지막 원소(`v[v.length-1]`)로 강제 클램핑하여 2.0으로 잘라냄.
2. **UI 렌더링 레이어 (`kabuki.js` & InnerTube `/youtubei/v1/next`)**:
   - "동영상 속도" 메뉴 항목은 InnerTube API 응답 내 `compactLinkRenderer`와 `setClientSettingEndpoint.settingDatas.intValue`로 구성된 8개 목록(0.25x ~ 2x).
   - `JSON.parse` 가로채기를 통해 해당 목록에 2.25x, 2.5x, 2.75x, 3.0x, 3.5x, 4.0x를 주입하면 UI 메뉴에 자연스럽게 렌더링되고 클릭 시 `setPlaybackRate`가 호출됨.

## 3. 세부 수정 계획

### A. `TVWebViewClient.kt` (플레이어 JS 정밀 패치)
- `this.nM = 2;` -> `this.nM = 4;`
- `this.nM=gm/100` -> `this.nM=Math.max(4,gm/100)`
- `AU1`의 상한선 및 `getAvailablePlaybackRates`가 자동으로 4.0까지 허용되도록 보장.

### B. `h5vcc_polyfill.js` (UI 메뉴 확장, 속도 제어 및 OSD)
- `sanitizeAdsDirectly(obj)`:
  - `compactLinkRenderer` 중 `clientSettingEnum.item === 'PLAYBACK_SPEED'`를 포함하는 배열을 감지하면 2.25x, 2.5x, 2.75x, 3.0x, 3.5x, 4.0x 항목을 자동 주입.
- `window.k2SetPlaybackRate(rate)` & `window.k2AdjustPlaybackRate(delta)`:
  - `<video>.playbackRate = rate` 설정.
  - `player.setPlaybackRate(rate)` 호출.
  - `localStorage['yt-player-playback-rate']` 및 `window._k2CurrentSpeed`에 보존.
  - 우상단 OSD 배지(`showSpeedOsd(rate)`) 호출 (부드러운 애니메이션 및 1.8초 자동 숨김).
- 영상 전환 복원:
  - `<video>`의 `playing` 이벤트 감지 시 `window._k2CurrentSpeed`가 1.0이 아니면 자동 복원.

### C. `TVRemoteKeyHandler.kt` (리모컨 핫키 연동)
- `KEYCODE_CHANNEL_UP`, `KEYCODE_PAGE_UP`, `KEYCODE_PROG_GREEN`: 속도 증가 (`k2AdjustPlaybackRate(1)`)
- `KEYCODE_CHANNEL_DOWN`, `KEYCODE_PAGE_DOWN`, `KEYCODE_PROG_RED`: 속도 감소 (`k2AdjustPlaybackRate(-1)`)
- `KEYCODE_PROG_YELLOW`: 1.0x 리셋 (`k2SetPlaybackRate(1.0)`)

## 4. 검증 계획
1. 빌드 성공 검증 (`.\gradlew.bat assembleDebug`).
2. TV 기기(`192.168.100.121:5555`)에 설치 (`adb install -r`).
3. TV 화면에서 "동영상 속도" 메뉴 진입 후 3배속 및 4배속 옵션 노출 확인.
4. 리모컨 및 메뉴를 통한 3배속 및 4배속 변경 시 OSD 배지 표시 및 실제 비디오 재생 속도 실시간 확인 (`video.playbackRate`).
5. 스크린샷 캡처 및 결과 리포트 작성.
