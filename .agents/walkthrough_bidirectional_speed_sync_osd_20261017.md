# 결과 리포트: 메뉴 속도 전환과 리모컨 속도 조절 간의 양방향 동기화 및 OSD 배지 보장

## 1. 개요 및 사용자 보고 현상
- **사용자 피드백**:
  > "4x 까지 생긴건 방금 확인했어. 그리고 일반으로 돌리니 속도가 1x로 돌아온 것도 확인했어.
  > 그런데, 리모콘으로 다시 Ch+를 누르면 기존 2x 상태였다면 2.25x 로 조정이 되거든. 즉, 컨트롤 옵션의 속도하고 연동을 못하고 있다는 거지. 그건 '일반'으로 돌릴 때, 오른쪽 화면 위에 1.0x 로 돌리지 못한다는 거겠지?"
- **문제 핵심**:
  - 설정 메뉴에서 마우스나 리모컨으로 속도를 '일반(1.0x)'으로 변경했을 때 비디오는 1.0배속으로 돌아오지만, 내부 상태 변수(`window._k2CurrentSpeed`)가 1.0으로 동기화되지 않고 이전 속도(예: 2.0x)로 유지됨.
  - 이로 인해 우상단에 `⚡ 1.0x (일반)` OSD 안내 배지가 뜨지 않았고, 직후 리모컨 `CH +` 버튼을 눌렀을 때 1.0x $\rightarrow$ 1.25x가 아니라 이전 속도(2.0x)의 다음 단계인 2.25x로 튀는 현상 발생.

---

## 2. 수술적 코드 수정 내역

### `app/src/main/assets/h5vcc_polyfill.js`
1. **`window._k2InternalRateChange` 락 플래그 도입**:
   - 리모컨 핫키(`k2SetPlaybackRate`) 호출 시 `_k2InternalRateChange = true`를 세워 중복 이벤트 및 불필요한 재귀 트리거를 방지하고, 완료 후 300ms 뒤 해제.
2. **`<video>`의 `ratechange` 이벤트 핸들러 추가**:
   - 외부 UI(컨트롤 설정의 속도 메뉴)에서 비디오의 `playbackRate`가 변경될 때 즉각 감지:
     ```javascript
     v.addEventListener('ratechange', function() {
         var r = Number(this.playbackRate);
         if (!isNaN(r) && r > 0) {
             if (!window._k2InternalRateChange && Math.abs((window._k2CurrentSpeed || 1.0) - r) > 0.01) {
                 window._k2CurrentSpeed = r;
                 try {
                     localStorage.setItem('yt-player-playback-rate', JSON.stringify({
                         data: String(r),
                         expiration: Date.now() + 86400000 * 30
                     }));
                 } catch (eLs) {}
                 k2ProtectAgainstStall(this);
                 showSpeedOsd(r);
             }
         }
     });
     ```
3. **`player.setPlaybackRate` 및 `k2OnSpeedChange` 래퍼에 `!window._k2InternalRateChange` 가드 적용**:
   - 내부 변경과 외부 UI 변경의 경로를 완벽히 분리하여 상태 정합성 보장.

---

## 3. 실제 Android TV 기기(`192.168.100.121:5555`) 실시간 검증 결과

### 1) 메뉴에서 1.0x (일반) 선택 시 실시간 동기화 및 OSD 배지 표출 검증
- 2.0x 상태에서 메뉴를 통해 1.0x(일반)로 전환한 즉시:
  - `window._k2CurrentSpeed` = 1.0으로 즉시 동기화됨.
  - 우측 상단에 `⚡ 1.0x (일반)` 컴팩트 배지가 안정적으로 표시됨.

![1.0x Normal Speed Badge on Menu Click](file:///C:/Users/k2love/.gemini/antigravity/brain/8dd04310-07b0-47f6-a489-f57745265845/tv_screen_badge_normal_sync.png)

### 2) 직후 리모컨 `CH +` 입력 시 정확한 1.25x 단계 이동 검증
- 1.0x 상태에서 리모컨 `CH +` 키를 눌렀을 때:
  - 2.25x로 튀지 않고, 1.0x의 다음 단계인 **1.25x**(`video.playbackRate = 1.25`, `window._k2CurrentSpeed = 1.25`)로 정확히 계산되어 이동함.
  - 우측 상단에 `⚡ 1.25x 속도` 배지가 즉각 표시됨.

![1.25x Speed Badge on Ch+ After Menu](file:///C:/Users/k2love/.gemini/antigravity/brain/8dd04310-07b0-47f6-a489-f57745265845/tv_screen_badge_125_sync.png)

### 3) CDP 런타임 상태 로그
```json
{
  "step1_2x_state": { "k2Speed": 2.0, "videoRate": 2.0 },
  "step2_menu_normal_selected": { "k2Speed": 1.0, "videoRate": 1.0, "badgeText": "⚡ 1.0x (일반)" },
  "step3_remote_ch_plus_pressed": { "k2Speed": 1.25, "videoRate": 1.25, "badgeText": "⚡ 1.25x 속도" }
}
```

---

## 4. 빌드 및 배포 상태
- Gradle 빌드: `.\gradlew.bat assembleDebug` 성공.
- TV 설치: `adb install -r YT_TV_AC.apk` 성공 (`192.168.100.121:5555`).
- Git 커밋 및 Push: 변경사항 반영 완료.
