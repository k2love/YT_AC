# 작업 진행 상황 (Task Board)

## 목표
1. **메뉴 속도 전환과 리모컨 속도 조절 간의 완벽한 양방향 동기화**:
   - 설정 메뉴(톱니바퀴 -> 속도 -> '일반' 또는 기타 배속) 선택 시 `window._k2CurrentSpeed`와 `video.playbackRate` 즉시 동기화.
   - 우측 상단에 `⚡ 1.0x (일반)` OSD 배지 즉각 표시.
   - 메뉴에서 속도를 변경한 직후 리모컨 `CH +` / `CH -` 조작 시 변경된 속도를 기준으로 다음/이전 단계로 정확히 이동하도록 보장.
2. **배속 전환 시 비디오 멎음(Stalling) 방지 및 신속 회복**.

---

## 작업 목록

- [x] **1. 현상 분석 및 원인 파악**
  - [x] 2.0x에서 메뉴로 1.0x 변경 시 `window._k2CurrentSpeed`가 2.0으로 잔류하고 OSD가 뜨지 않던 원인 규명 (`ratechange` 리스너 부재)
  - [x] 리모컨 핫키와 메뉴 변경 간 무한 루프 방지 전략 수립 (`_k2InternalRateChange` 플래그 도입)
- [x] **2. 수술적 코드 수정**
  - [x] `app/src/main/assets/h5vcc_polyfill.js`:
    - `window._k2InternalRateChange` 플래그 관리
    - `<video>` `ratechange` 이벤트 핸들러 구현 (외부 UI 변경 시 `_k2CurrentSpeed` 동기화, `localStorage` 저장, `k2ProtectAgainstStall`, `showSpeedOsd`)
    - `player.setPlaybackRate` 및 `k2OnSpeedChange` 가드 처리
- [x] **3. 빌드 및 배포**
  - [x] Gradle 빌드: `.\gradlew.bat assembleDebug` 성공
  - [x] TV 기기 설치: `adb install -r YT_TV_AC.apk` 성공 (`192.168.100.121:5555`)
- [x] **4. 실제 TV 실시간 검증**
  - [x] 메뉴에서 '일반(1.0x)' 선택 시 `⚡ 1.0x (일반)` OSD 배지 노출 및 `k2Speed: 1.0` 동기화 확인 (`tv_screen_badge_normal_sync.png`)
  - [x] 직후 리모컨 `CH +` 입력 시 2.25x가 아닌 정확히 1.25x로 단계 이동 및 `⚡ 1.25x 속도` 배지 노출 확인 (`tv_screen_badge_125_sync.png`)
- [x] **5. 문서화 및 버전 관리**
  - [x] `.agents/implementation_plan_bidirectional_speed_sync_osd_20261017.md` 작성
  - [x] `.agents/walkthrough_bidirectional_speed_sync_osd_20261017.md` 작성
  - [ ] Git commit & push
