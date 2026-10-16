# 구현 계획서: 컴팩트 우상단 OSD 속도 배지 복원 및 고배속 다운시프트 시 비디오 멎음 방지

## 1. 개요 및 배경
- 사용자가 TV 리모컨의 채널(`CH +` / `CH -`) 버튼으로 속도를 조절할 때 우상단에 표시되던 현재 재생속도 안내가 뜨지 않는 문제를 해결하고, 기존의 다소 컸던 배지를 약간 더 아담하고 컴팩트한 크기로 개선합니다.
- 2배속 이상으로 재생하다가 설정 메뉴(또는 핫키)에서 '일반(1.0x)'으로 속도를 낮췄을 때 영상이 멎는(stalled/paused) 현상을 방지하여 매끄러운 시청 경험을 보장합니다.

---

## 2. 세부 원인 분석

### 1) 우상단 OSD 배지 미노출 원인
- `showSpeedOsd`는 `document.body.appendChild(badge)` 형태로 삽입되나, YouTube TV의 Leanback 렌더러는 전체 화면 비디오 컨테이너(`ytlr-player__player-container-player` 또는 `#player`) 위에 여러 계층의 레이어와 풀스크린 요소를 띄웁니다.
- `z-index: 9999999`로 설정되어 있더라도, 부모 컨텍스트나 풀스크린 상태, 또는 CSS 애니메이션(`transform: translateY(-10px) scale(0.95)`)의 타이밍과 기존 엘리먼트 재활용 문제로 인해 보이지 않거나 가려질 수 있습니다.
- 또한 사용자의 "약간 작은 안내면 좋겠어"라는 요구에 맞게 배지의 크기(폰트 18px, 패딩 8px 18px, 둥근 모서리 8px, 네온 테두리)를 컴팩트하게 재조정하고, `document.fullscreenElement || document.body` 최상단에 안정적으로 주입되도록 개선합니다.

### 2) 고배속 -> 일반(1.0x) 전환 시 비디오 멎음 원인
- Chromium 하드웨어 가속 비디오 파이프라인에서 배속을 2.0x~4.0x에서 급격히 1.0x로 낮출 때:
  - 디코더 버퍼 타임스탬프와 렌더러 클럭의 불일치로 인해 브라우저 HTML5 `<video>`가 일시적으로 `waiting` 또는 내부 버퍼 언더런 상태에 진입하여 재생이 멈추거나 `paused` 상태로 방치될 수 있습니다.
  - 플레이어의 내부 레이트 전환 처리 후 즉시 `if (v.paused) v.play()`를 안전하게 호출해주고, `stalled`/`waiting` 이벤트 발생 시 부드럽게 킥을 날려주어 멎는 현상을 완벽하게 방지합니다.

---

## 3. 수술적 수정 계획

### 1) `app/src/main/assets/h5vcc_polyfill.js`
- **컴팩트 OSD UI 리팩토링**:
  - `showSpeedOsd(rate)`:
    - 폰트 크기: `28px` -> `18px`
    - 아이콘 크기: `32px` -> `20px`
    - 패딩: `12px 26px` -> `8px 18px`
    - 위치: `top: 36px`, `right: 36px`
    - `z-index`: `2147483647` (최대 32비트 정수)
    - 부모 엘리먼트: `(document.fullscreenElement || document.body)`
    - 기존 노드가 있더라도 확실하게 DOM 트리의 최상위에 올라오도록 재배치(`appendChild`).
- **속도 변경 시 비디오 재생 멎음 방지(Stall Recovery)**:
  - `k2SetPlaybackRate` 및 `k2OnSpeedChange`:
    - 배속 변경 직후 및 50ms/150ms 딜레이 후 `if (v.paused) v.play().catch(...)` 호출.
    - 다운시프트(예: 2x -> 1x) 시 비디오가 멈칫하는 현상을 방지하기 위해 `waiting`/`stalled` 임시 이벤트 핸들러를 가동하여 100ms 내에 재생을 재개하도록 보장.

### 2) `app/src/main/java/com/k2/youtubetv/remote/TVRemoteKeyHandler.kt`
- 채널 업/다운 이벤트 수신 시 로그 및 웹뷰 스레드 안전 호출 확인.

---

## 4. 검증 계획
1. `.\gradlew.bat assembleDebug` 빌드 검증.
2. `adb install -r YT_TV_AC.apk` 기기 배포.
3. TV에서 리모컨 `CHANNEL_UP` / `CHANNEL_DOWN` 입력 시 우상단에 아담하고 컴팩트한 OSD 배지가 정확히 표시되는지 스크린샷 캡처 (`tv_screen_compact_badge.png`).
4. 고배속(2x, 3x) 재생 상태에서 설정 메뉴를 열어 '일반'을 선택했을 때 비디오가 멎지 않고 부드럽게 1.0배속으로 이어지는지 실시간 검증.
