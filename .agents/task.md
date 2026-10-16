# 작업 보드: YouTube TV 재생 속도 제한 완전 해제 (최대 4배속 및 3배속 지원, UI 메뉴 확장 및 리모컨 핫키 연동)

## 1. 개요 및 사용자 요구사항
- **현상**:
  - YouTube TV 플레이어에서 기본 재생 속도가 2.0배속으로 제한(Cap)되어 있음.
  - 플레이어 설정의 "동영상 속도" 메뉴에서도 0.25배부터 최대 2배까지만 노출됨.
- **목표**:
  - 사용자 요청: "2x에서 제한 걸려있는 거 같은데? 3x 까지 제한 해제해봐. 4배속도 가능하다면 해줘."
  - 3.0배속을 포함하여 최대 4.0배속(2.25x, 2.5x, 2.75x, 3.0x, 3.5x, 4.0x)까지 속도 제한 완전 해제.
  - YouTube TV UI의 "동영상 속도" 메뉴에 확장 속도 옵션 자동 주입 및 정상 동작 연동.
  - TV 리모컨 원터치 속도 조절 핫키(채널 상/하, 페이지 상/하, 컬러키) 및 우상단 세련된 속도 OSD 배지 구현.
  - 다음 영상 전환 시 사용자 설정 속도 지속 유지.
  - 실제 Android TV 기기(`192.168.100.121:5555`)에서 실시간 검증 및 캡처.

## 2. 작업 단계
- [x] 1. 속도 제한 구조 역공학 분석 (`tv-player-ias.js`, `kabuki.js`, InnerTube `PLAYBACK_SPEED` renderer)
- [x] 2. 실제 TV MSE/하드웨어 비디오 디코더 3x 및 4x 재생 가능 여부 검증 (정상 동작 확인)
- [x] 3. 사전 베이스라인 빌드 검증 (`.\gradlew.bat assembleDebug` 성공)
- [x] 4. `implementation_plan_unlock_playback_speed_4x_20261017.md` 계획서 작성
- [x] 5. `TVWebViewClient.kt` 플레이어 번들 패치 적용 (`this.nM=4`, `maximumPlaybackRate` 400 해제)
- [x] 6. `h5vcc_polyfill.js` 속도 제한 해제 로직 구현:
  - InnerTube `PLAYBACK_SPEED` 렌더러 메뉴 자동 확장 (2.25x ~ 4.0x)
  - `player.getAvailablePlaybackRates` 4.0x 래핑
  - `window.k2SetPlaybackRate` / `window.k2AdjustPlaybackRate` 구현
  - 우상단 속도 OSD 배지 UI 구현
  - 영상 전환 시 속도 유지 로직
- [x] 7. `TVRemoteKeyHandler.kt` 리모컨 핫키 연동 (채널 Up/Down, Page Up/Down, Color Keys)
- [x] 8. 사후 빌드 확인 (`.\gradlew.bat assembleDebug`)
- [x] 9. TV 기기(`192.168.100.121:5555`) APK 배포 및 설치
- [x] 10. 실제 TV에서 3배속 및 4배속 재생, UI 메뉴, OSD 배지 실시간 검증 및 캡처
- [x] 11. 결과 리포트 (`walkthrough_unlock_playback_speed_4x_20261017.md`) 작성
- [x] 12. Git 커밋 및 푸시
