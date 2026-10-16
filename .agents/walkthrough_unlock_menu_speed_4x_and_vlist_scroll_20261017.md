# 결과 리포트: 설정 메뉴 동영상 배속 4.0x 잠금 해제 및 가상 리스트 스크롤 연동

## 1. 개요 (Overview)
- **작업 목적**:
  - 플레이어 설정(톱니바퀴) $\rightarrow$ '동영상 속도' 메뉴에서 2.0x 초과 배속(2.25x ~ 4.0x) 옵션이 리모컨 및 마우스로 원활히 스크롤되고 선택될 수 있도록 가상 리스트(`yt-virtual-list`)의 렌더링 한계를 극복.
  - 메뉴에서 2.25x ~ 4.0x 옵션을 선택했을 때, 플레이어 코어 검증 로직에 의해 2.0x로 강제 절삭(클램프)되지 않고 선택한 속도가 실제 영상 재생 속도(`video.playbackRate`), 플레이어 내부 상태, `localStorage`, 우측 상단 OSD 배지에 1:1로 완벽 동기화되도록 보장.
- **검증 환경**:
  - 실기 Android TV (`192.168.100.121:5555`)
  - Chrome DevTools Protocol (CDP) 및 ADB 입력 제어
  - 사용자 실시간 모니터링 및 성공 판정 완료

---

## 2. 근본 원인 분석 (Root Cause Analysis)

### 원인 1: 플레이어 번들(`tv-player-ias-tcl.js`) 내부의 `NF` 속도 클램프
- 플레이어 내부 속도 설정 함수 `NF`에서 가용 재생 속도 목록 `F = getAvailablePlaybackRates()`를 조회한 뒤 `F[F.length - 1]`(최댓값)를 추출하여 `a >= F ? G = F` 로 강제 클램프하고 있었음.
- 가용 속도 필터 함수(`return oBf.filter(function(a){return a>=L&&a<=g})`)에서 비디오 메타데이터 `N.Cj`가 2.0으로 고정되어 있어 `F` 배열의 최댓값이 항상 2.0이었음.
- 이로 인해 메뉴에서 3x, 4x를 선택해도 플레이어 코어가 2.0x로 값을 깎아버림.

### 원인 2: 가상 리스트(`yt-virtual-list` / `mH`) 위치 배열 메모이제이션 고착
- 유튜브 TV의 가상 리스트 컴포넌트는 초기 8개 항목(0.25x ~ 2.0x)의 위치 정보를 `snapshot.positions`에 저장하고 이를 캐시(`j.G`)하여 8번 인덱스 이후로 포커스가 아래로 이동하지 못하도록 방어하고 있었음.

---

## 3. 수술적 해결 방안 (Surgical Solution)

### A. 플레이어 코어 속도 검증 로직 패치 ([TVWebViewClient.kt](file:///E:/AI_Projects/%23%23%20YouTube%20TV%20for%20Android%20Clone/app/src/main/java/com/k2/youtubetv/webview/TVWebViewClient.kt))
- `PATCH_VERSION`: 3 $\rightarrow$ 5 로 증가시켜 웹뷰 캐시 완전 무효화.
- **`NF` 클램프 상한선 해제**:
  - `F=F[F[v[l^3812]]-1];a<=G||(a>=F?G=F:` $\rightarrow$ `F=Math.max(4,F[F[v[l^3812]]-1]);a<=G||(a>=F?G=F:`
- **가용 배속 필터 상한선 해제**:
  - `var L=N.jW,g=N.Cj;return oBf.filter(...)` $\rightarrow$ `var L=N.jW,g=Math.max(4,N.Cj||2);return oBf.filter(...)`
- **배속 사다리에 세부 배속 추가**:
  - `oBf=s1f.concat([2.5,3,3.5,4])` $\rightarrow$ `oBf=s1f.concat([2.25,2.5,2.75,3,3.5,4])`

### B. 가상 리스트 스냅샷 및 라디오 버튼 동기화 ([h5vcc_polyfill.js](file:///E:/AI_Projects/%23%23%20YouTube%20TV%20for%20Android%20Clone/app/src/main/assets/h5vcc_polyfill.js))
- **스냅샷 갱신**: 가상 리스트 인스턴스 `vInst.j.G = vInst.j.B`로 메모이제이션을 우회하고, 항목 수가 8개를 초과할 때 `vInst.A()`를 트리거하여 14개 전체 항목의 스냅샷 생성.
- **라디오 버튼 동기화**: `window._k2CurrentSpeed`와 일치하는 배속 항목의 `iconType`을 `RADIO_BUTTON_CHECKED`로 실시간 반영.

---

## 4. 검증 결과 (Verification Results)

1. **메뉴 스크롤 및 4x 선택 성공**:
   - 설정 $\rightarrow$ '동영상 속도' 메뉴에서 `1.75×`, `2×`, `2.25×`, `2.5×`, `2.75×`, `3×`, `3.5×`, `4×`까지 막힘없이 스크롤 노출 확인.
   - `4×` 선택 시 `videoPlaybackRate: 4`, `playerPlaybackRate: 4`, `k2Speed: 4` 즉시 반영.
   - 우측 상단 OSD 배지에 `⚡ 4x 속도` 정상 표시.
2. **리모컨 Ch+/Ch- 및 양방향 제어**:
   - 리모컨 채널 버튼으로 0.25x 단위 미세 조절과 메뉴 옵션 선택이 완벽하게 상호 연동됨.
3. **사용자 실기 조작 검증 완료**:
   - 실제 TV 환경에서 사용자가 직접 리모컨으로 메뉴 조작 및 배속 변경 정상 동작 확인 완료.

---

## 5. 결론 및 산출물
- **빌드 산출물**: [YT_TV_AC.apk](file:///E:/AI_Projects/%23%23%20YouTube%20TV%20for%20Android%20Clone/YT_TV_AC.apk)
- **수정 소스**:
  - [TVWebViewClient.kt](file:///E:/AI_Projects/%23%23%20YouTube%20TV%20for%20Android%20Clone/app/src/main/java/com/k2/youtubetv/webview/TVWebViewClient.kt)
  - [h5vcc_polyfill.js](file:///E:/AI_Projects/%23%23%20YouTube%20TV%20for%20Android%20Clone/app/src/main/assets/h5vcc_polyfill.js)
