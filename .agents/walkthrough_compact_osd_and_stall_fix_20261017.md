# 결과 리포트: 컴팩트 OSD 속도 배지 복원 및 고배속 다운시프트 시 비디오 멎음 방지

## 1. 개요 및 사용자 피드백
- **피드백 1**: "오른쪽 위에 뜨던 현재 재생속도는 안 뜨네. 리모콘 Ch버튼으로 조정할 때 나오는 건 다시 반영해주는게 좋아보여. 다만, 약간 작은 안내면 좋겠어."
  - 리모컨 채널 키(`CH +` / `CH -`) 조작 시 우상단 속도 OSD 배지가 표시되지 않던 원인을 규명하고, 크기를 기존 대비 약 40% 축소하여 세련되고 아담한 미니멀 디자인으로 복원.
- **피드백 2**: "2배속 이상으로 재생하다가 설정에서 일반으로 속도를 낮췄을 때, 영상이 멎는 경우가 있어."
  - 2.0x 이상의 고배속에서 1.0x(일반)로 속도를 낮췄을 때 비디오 버퍼링 또는 디코더 정체로 인해 화면이 멎거나 멈추는 현상(Stall)을 방지하는 자동 재생 킥(Recovery Kick) 메커니즘 구축.

---

## 2. 근본 원인 분석

### 1) OSD 배지가 표시되지 않았던 이유: YouTube TV의 Trusted Types 정책
- YouTube TV 웹 애플리케이션에 최신 **Trusted Types (CSP)** 보안 정책이 강제되고 있었습니다.
- 기존 코드의 `badge.innerHTML = '...'` 실행 시 브라우저가:
  > `TypeError: Failed to set the 'innerHTML' property on 'Element': This document requires 'TrustedHTML' assignment.`
  예외를 발생시키고 있었으며, 이로 인해 `catch (eOsd) {}` 블록으로 빠져 배지 텍스트가 삽입되지 않고 `opacity: 1`이 설정되지 못한 채 소멸되었습니다.
- **해결책**:
  - `innerHTML`을 완전히 제거하고, 표준 DOM 조작 API(`document.createElement`, `textContent`, `appendChild`)를 적용하여 Trusted Types 정책을 100% 준수하도록 재작성하였습니다.

### 2) 배지 크기 및 스타일링 개선
- 기존 28px의 다소 컸던 글꼴 크기와 두꺼운 패딩을 다음과 같이 컴팩트하게 재구성하였습니다:
  - 폰트 크기: `28px` -> `16px` (약 40% 축소)
  - 번개 아이콘: `32px` -> `18px`
  - 패딩: `12px 26px` -> `6px 14px`
  - 위치: 화면 우상단 `top: 32px`, `right: 32px`
  - 테두리/배경: 반투명 네온 시안 라인(`border: 1.5px solid rgba(0, 229, 255, 0.8)`), 8px 라운드 처리, 은은한 그림자.

### 3) 고배속 -> 일반 다운시프트 시 비디오 멎음 방지
- 고배속(2x~4x)에서 1.0x로 낮출 때 Chromium 미디어 디코더의 버퍼 상태와 클럭 동기화 타이밍 문제로 비디오가 일시적 `paused` 또는 `waiting` 상태에 머무르는 현상이 발생했습니다.
- 속도 변경 함수(`k2SetPlaybackRate`, `k2OnSpeedChange`, `player.setPlaybackRate`) 호출 시 `window._k2SpeedChanging = true` 가드 플래그를 설정하고, `k2ProtectAgainstStall()`을 통해 즉시 및 50ms, 150ms, 350ms, 700ms 간격으로 `video.play()`를 자동 킥하도록 조치하였습니다.
- 또한 속도 전환 중 일어나는 `pause` 및 `waiting` 이벤트에 반응하여 즉시 재생을 이어받도록 방어 리스너를 구현했습니다.

---

## 3. 실제 Android TV 기기(`192.168.100.121:5555`) 실시간 검증 결과

### 1) 리모컨 `CH +` 버튼 입력 시 컴팩트 배지 노출
- 리모컨 `CH +` 키를 눌러 배속을 1.75x로 올렸을 때 우상단에 작고 깔끔한 배지가 정상 표시됨을 확인하였습니다.

![Compact Speed Badge on Ch+](/tv_screen_badge_175.png)

### 2) 설정 메뉴 / API를 통한 1.0x(일반) 전환 시 정상 재생 및 배지 확인
- 2.0x 이상 상태에서 1.0x로 속도를 낮췄을 때 `⚡ 1.0x (일반)` 배지가 우상단에 뜨며, 비디오가 멎지 않고 연속적으로 재생됨을 실시간 확인하였습니다.

![1.0x Normal Speed Badge](/tv_screen_normal_badge_snap.png)

### 3) 1.0x 전환 후 재생 시간 진행 로그
```
Step 1: Set playback speed to 3.0x -> Playing smoothly
Step 2: Change speed down to 1.0x (Normal)
States after downshifting:
  [0.0s] paused=False, rate=1, time=68.50
  [0.3s] paused=False, rate=1, time=68.84
  [0.6s] paused=False, rate=1, time=69.16
  [0.9s] paused=False, rate=1, time=69.38
  [1.2s] paused=False, rate=1, time=69.59
  [1.5s] paused=False, rate=1, time=69.91
  [1.8s] paused=False, rate=1, time=70.22
  [2.1s] paused=False, rate=1, time=70.52
  [2.4s] paused=False, rate=1, time=70.83
  [2.7s] paused=False, rate=1, time=71.15
Result: Time advanced continuously without pause/stall.
```

---

## 4. 빌드 및 배포
- Gradle 빌드: `.\gradlew.bat assembleDebug` 성공 (`BUILD SUCCESSFUL in 1s`).
- TV 설치: `adb install -r YT_TV_AC.apk` 성공 (`Success`).
