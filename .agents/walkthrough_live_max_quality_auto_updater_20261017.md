# 결과 보고서: 라이브 방송 1080p60 및 4K/8K 초고화질 제한 완전 해제 & 자동 상향

## 1. 개요
- **사용자 요청 사항**:
  1. 라이브 방송을 재생할 때 실제 1080p 이상 송출 방송임에도 420p(480p)로 화질이 고정되는 현상 해결.
  2. 4K, 8K 관광/고화질 영상 시청 시 720p로 고정(Capping)되는 모든 제한을 완전히 풀고 최고 화질로 자동 선택/업데이트 적용.
- **작업 일시**: 2026-10-17
- **검증 환경**: Android TV 실기기 (`192.168.100.121:5555`)

---

## 2. 역공학 분석 및 근본 원인 규명
유튜브 공식 TV 웹 플레이어 번들(`tv-player-ias.js`, 2.4MB)을 역공학하여 다음 핵심 로직을 발견했습니다:

1. **HFR (60fps) 검사 및 `capHfr` 발동**:
   - `if (!v.Fx && !HH(v, j6.FRAMERATE)) return "capHfr";`
   - 유튜브 플레이어는 60fps 포맷을 재생하기 전에 디바이스가 정직하게 응답하는지 검사하는 **Sanity Probe**를 실행합니다.
   - `HH(v, j6.FRAMERATE) = isTypeSupported('... framerate=30') && !isTypeSupported('... framerate=9999')`
2. **Chromium WebView MSE의 버그/동작 차이**:
   - 안드로이드 WebView는 불가능한 파라미터(`framerate=9999`, `height=99999`, `bitrate=2E9` 등)에도 무조건 `true`를 반환합니다.
   - 이로 인해 `!isTypeSupported(... framerate=9999)`가 `false`가 되어 `HH` 검사가 실패합니다.
   - 플레이어는 디바이스가 거짓말을 한다고 판단하여 **`capHfr`을 발동, 30fps 초과(60fps) 포맷(1080p60, 720p60 등)을 스트림 목록에서 모조리 삭제**하여 30fps인 480p 이하만 남게 되었습니다.
3. **4K/8K 720p 고정 현상**:
   - 4K 영상도 대다수가 60fps(예: `LXb3EKWsInQ`)이므로 동일하게 60fps 포맷이 삭제되고 30fps 중 최고 화질인 720p로 강등되었습니다.

---

## 3. 수술적 정밀 수정 내역 (`h5vcc_polyfill.js`)

### A. 스마트 Sanity Probe 방어 (`MediaSource.isTypeSupported`)
- 플레이어의 검사 규격(`j6`)에 맞춰 불가능한 가짜 프로브에 대해 명시적 `false`를 반환하고, 정상 범위의 코덱 쿼리에 대해 `true`를 반환하도록 방어 계층을 구축했습니다.
  ```javascript
  var fpsM = lower.match(/framerate\s*=\s*(\d+)/);
  if (fpsM && parseInt(fpsM[1], 10) > 120) return false;

  var hM = lower.match(/height\s*=\s*(\d+)/);
  if (hM && parseInt(hM[1], 10) > 4320) return false;

  var wM = lower.match(/width\s*=\s*(\d+)/);
  if (wM && parseInt(wM[1], 10) > 7680) return false;

  var brM = lower.match(/bitrate\s*=\s*(\d+)/);
  if (brM && parseInt(brM[1], 10) >= 20000000) return false;

  var chM = lower.match(/channels\s*=\s*(\d+)/);
  if (chM && parseInt(chM[1], 10) > 8) return false;

  if (lower.indexOf('catavision') !== -1 ||
      lower.indexOf('invalidformat') !== -1 ||
      lower.indexOf('decode-to-texture=nope') !== -1 ||
      lower.indexOf('av99') !== -1 ||
      lower.indexOf('experimental=invalid') !== -1 ||
      lower.indexOf('tunnelmode=false') !== -1) {
      return false;
  }
  ```

### B. 최고 화질 점진적 자동 상향 (`k2AutoBoostQuality`)
- 영상 재생 시작 및 진행 중 사용 가능한 최고 화질을 감지하여 점진적으로 최상위 화질로 자동 선택(`setPlaybackQuality`, `setPlaybackQualityRange`)합니다.
- 사용자가 수동으로 저화질을 선택했을 때는 이를 덮어쓰지 않도록 랭크 기반 보호 로직을 탑재했습니다.

### C. 8K/4K/1080p 전체 화질 메뉴 노출 및 정렬
- `adaptiveFormats`에 존재하는 8K(`hd4320`), 4K(`hd2160`), 1440p, 1080p가 누락 없이 메뉴에 나타나며, 내림차순으로 깔끔하게 정렬됩니다.

---

## 4. 실기기 검증 결과 (Android TV `192.168.100.121:5555`)

### 1) 라이브 방송 (`OsqH1F_BL1I`, 문호준 라이브 생방송)
- **적용 전**: 420p/480p 고정, 1080p 선택 불가
- **적용 후 실시간 검증 (Stats for Nerds)**:
  - `q`: **`hd1080`**
  - `resolution`: **`1920x1080@60 / 1920x1080@60` (HFR 60fps 정상 수신)**
  - `codecs`: **`vp09.00.51.08.01.01.01.01.00 (303)` (1080p60 VP9 itag)**
  - `live_mode`: `Manifestless, Optimized for Low Latency`
  - `availableQualityLevels`: `['hd1080', 'hd720', 'large', 'medium', 'small', 'auto']`

### 2) 4K 60fps HDR 관광 영상 (`LXb3EKWsInQ`, Costa Rica 4K 60fps HDR)
- **적용 전**: 720p로 고정
- **적용 후 실시간 검증 (Stats for Nerds)**:
  - `q`: **`hd2160`**
  - `resolution`: **`3840x2160@60 / 3840x2160@60` (4K 60fps Ultra HD)**
  - `codecs`: **`av01.0.13M.10.0.110.09.16.09.0 (701) / opus (251)` (AV1 4K60 HDR)**
  - `availableQualityLevels`: `['hd2160', 'hd1440', 'hd1080', 'hd720', 'large', 'medium', 'small', 'tiny', 'auto']`

---

## 5. 결론
유튜브 TV 플레이어가 안드로이드 웹뷰의 비표준 동작으로 인해 오작동하던 HFR(60fps) 차단 필터를 역공학 분석을 통해 완전히 정상화시켰으며, 라이브 및 초고화질 관광 영상 모두에서 기기가 지원하는 최고 화질(1080p60, 4K60 HDR)로 자동 상향되어 재생됨을 확인하였습니다.
