# 구현 계획서: 라이브 및 4K/8K 고화질 영상 전체 화질 캡(Cap) 해제 및 최고 화질 자동 선택 로직 구현

## 1. 개요 및 역공학 분석 결과
사용자 피드백에 따라 다음 두 가지 치명적인 화질 제한 문제를 해결합니다:
1. **라이브 방송 1080p60 스트림 존재에도 480p(large) 고정 문제**
2. **4K, 8K, 16K 관광/고화질 영상이 720p(hd720)로 캡핑되는 문제**

### 🔍 REA 및 플레이어 번들(`tv-player-ias.js`) 역공학 핵심 발견
- **Chromium MSE와 YouTube TV 플레이어 간 프로브 판정 불일치 버그 규명**:
  - 유튜브 플레이어는 HFR(60fps)과 고해상도 지원 여부를 판별할 때 플랫폼의 정직성을 테스트하는 **Sanity Probe**를 수행합니다:
    `HH(v, j6.FRAMERATE) = N.isTypeSupported('... framerate=30') && !N.isTypeSupported('... framerate=9999')`
  - 하지만 안드로이드 WebView의 네이티브 Chromium MSE는 파라미터를 무시하고 `framerate=9999` 같은 불가능한 값에도 `true`를 반환합니다.
  - 이로 인해 `!isTypeSupported(... 9999)`가 `false`가 되어 `HH(v, j6.FRAMERATE)`가 **`false`**로 떨어지고, 플레이어가 **`return "capHfr"`**을 발동하여 60fps(HFR) 포맷 전체(1080p60, 720p60, 4K60 등)를 스트림 목록에서 모조리 삭제(filter out)했습니다.
  - 그 결과 60fps로 송출되는 모든 라이브 방송과 4K 60fps 관광 영상이 30fps인 480p 이하 또는 720p 30fps로 강제 고정되었습니다.

---

## 2. 변경 대상 및 수술적 수정 상세 계획

### 1) 대상 파일
- [`app/src/main/assets/h5vcc_polyfill.js`](file:///E:/AI_Projects/##%20YouTube%20TV%20for%20Android%20Clone/app/src/main/assets/h5vcc_polyfill.js)

### 2) 핵심 수정 사항

#### (1) `MediaSource.isTypeSupported` 스마트 Sanity Probe 보정
- 불가능한 가짜 프로브(`framerate > 120`, `height > 4320`, `width > 7680`, `bitrate >= 20000000`)에 대해 명시적으로 **`false`**를 반환.
- 정상적인 하드웨어 디코딩 범위 내(`framerate <= 120`, `height <= 4320`, `width <= 7680`)의 VP9, AV1, AVC1 코덱 요청에 대해 **`true`**를 반환.
- **효과**: `capHfr` (60fps 제한), `mvhcap` (최대 세로 해상도 제한), `ratecap` (비트레이트 제한), `blk8khfr` (8K HFR 차단)이 원천 해제되어 1080p60, 1440p60, 2160p60, 4320p 포맷이 100% 온전히 보존됨.

#### (2) 최고 화질 자동 선택 및 부스터 (`k2AutoBoostQuality`)
- 비디오 재생 시점(로드 완료 및 메타데이터 로드)에 현재 스트림의 `availableQualityLevels`를 분석.
- 사용 가능한 최고 화질(예: `hd2160`, `hd1440`, `hd1080`)을 탐색하여:
  - `player.setPlaybackQualityRange(maxQuality, maxQuality)`
  - `player.setPlaybackQuality(maxQuality)`
  - 를 호출하여 라이브 및 VOD가 시작 즉시 최고 화질로 락(Lock)/전환되도록 자동 최적화.

#### (3) 화질 선택 메뉴 (`getAvailableQualityLevels` & `getAvailableQualityData`) 완전 개방
- 플레이어의 `streamingData.adaptiveFormats`에 존재하는 모든 고화질(4K, 1440p, 1080p, 720p)이 리모컨 화질 변경 메뉴에 온전히 표출되도록 데이터 브릿지 보강.

---

## 3. 검증 계획
1. **빌드 검증**: `.\gradlew.bat assembleDebug` 성공 확인.
2. **원격 배포**: ADB로 TV 기기(`192.168.100.121:5555`)에 설치 및 앱 재시작.
3. **실제 라이브 방송 검증**:
   - 라이브 방송(`OsqH1F_BL1I`) 재생 시 `availableQualityLevels`에 `hd1080`, `hd720`이 정상 포함되는지 확인.
   - 비디오 해상도가 854x480(480p)에서 **1920x1080(1080p60)**으로 자동 상향되어 재생되는지 전문 통계(Stats for nerds) 및 캡처로 검증.
4. **4K/8K 60fps 고화질 관광 영상 검증**:
   - 4K 60fps 영상 재생 시 720p가 아닌 **3840x2160(2160p60)**으로 정상 재생되는지 캡처 검증.
5. **결과 리포트 작성 및 원격 Git 푸시**.
