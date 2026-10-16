# 작업 보드: 라이브 방송 480p 고정 해결 및 4K/8K/HFR 화질 제한 완전 해제

## 1. 개요 및 사용자 요구사항
- **현상**:
  1. 라이브 방송(Live Stream)을 재생할 때 실제 1080p 이상 송출되는 방송임에도 불구하고 420p/480p로 화질이 고정되는 문제.
  2. 4K, 8K 관광/고화질 영상 재생 시 720p 등으로 화질이 고정/제한(cap)되는 문제.
- **목표**:
  1. 오리지널 유튜브 TV 앱의 번들 역공학(`tv-player-ias.js`)을 통한 HFR(60fps) 및 화질 제한 근본 원인(`capHfr`, `MediaSource.isTypeSupported` Sanity Probe) 규명.
  2. Chromium MSE Sanity Probe 방어 패치 적용하여 `capHfr` 및 HDR 드롭 원천 차단.
  3. 라이브 및 일반 VOD 재생 시 사용 가능한 최고 화질(1080p60 / 4K60 / 8K 등)로 즉시 자동 상향(Auto-boost)하는 업데이터 로직 적용.
  4. 실제 Android TV 기기(`192.168.100.121:5555`)에서 실시간 라이브 방송(`OsqH1F_BL1I`) 및 4K 60fps HDR 영상(`LXb3EKWsInQ`)을 직접 재생하여 각각 1080p@60, 2160p@60으로 구동되는지 Stats for Nerds 검증 완료.

## 2. 작업 단계
- [x] 1. 기존 비디오 플레이어 및 화질 관련 코드 정밀 분석 (`h5vcc_polyfill.js`, `MainActivity.kt` 등)
- [x] 2. 오리지널 유튜브 TV 앱 / Cobalt 플레이어의 라이브 스트리밍 화질 결정 및 ABR 제어 로직 분석 (`tv-player-ias.js`)
- [x] 3. `implementation_plan_unlock_all_qualities_and_live_hfr_20261017.md` 계획서 작성
- [x] 4. Sanity Probe 방어 및 최고 화질 자동 선택 / ABR 부스트 로직 구현 (`h5vcc_polyfill.js`)
- [x] 5. Gradle 빌드 성공 확인 (`.\gradlew.bat assembleDebug`)
- [x] 6. TV 기기(`192.168.100.121:5555`)에 APK 배포 및 설치
- [x] 7. 실제 라이브 방송 및 4K 영상 재생 후 통계(Stats for nerds) 캡처 검증 (1080p@60, 2160p@60)
- [x] 8. `walkthrough_live_max_quality_auto_updater_20261017.md` 결과 리포트 작성
- [ ] 9. Git 커밋 및 `origin/main` 푸시
