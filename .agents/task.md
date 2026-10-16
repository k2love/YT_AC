# 작업 진행 상황 (Task Board)

## 목표
1. **플레이어 설정(톱니바퀴) -> '동영상 속도' 메뉴에서 2.0x 초과 배속(2.25x ~ 4x) UI 노출 및 스크롤 잠금 해제**:
   - 가상 리스트(`yt-virtual-list` / `mH`)의 위치 배열 메모이제이션 고착을 우회하고 스냅샷을 14개로 갱신하여 2.0x 아래로 리모컨 방향키 스크롤 보장.
2. **플레이어 속도 클램프 완전 해제 (최대 4.0x 허용)**:
   - 메뉴에서 2.25x ~ 4x 선택 시 플레이어 내부 `NF` 클램프와 `oBf` 가용 배속 필터에 의해 2.0x로 절삭되지 않고 선택한 배속으로 즉시 전환 보장.
3. **현재 배속 라디오 버튼 선택 상태 동기화 및 OSD 배지 실시간 연동**.

---

## 작업 목록

- [x] **1. 수술적 코드 수정**
  - [x] `app/src/main/java/com/k2/youtubetv/webview/TVWebViewClient.kt`:
    - `PATCH_VERSION`: 3 -> 5 (웹뷰 캐시 완전 무효화)
    - `NF` 클램프 상한선 4.0x 패치 (`F=Math.max(4,F[F[v[l^3812]]-1]);a<=G||(a>=F?G=F:`)
    - `oBf.filter` 가용 배속 상한선 4.0x 패치 (`var L=N.jW,g=Math.max(4,N.Cj||2);return oBf.filter(...)`)
    - `oBf` 배속 사다리에 `2.25` 및 `2.75` 추가 (`oBf=s1f.concat([2.25,2.5,2.75,3,3.5,4])`)
  - [x] `app/src/main/assets/h5vcc_polyfill.js`:
    - `k2ExpandSpeedItemsInArray`: 2.0x 초과 배속 활성화 시 라디오 버튼 상태(`RADIO_BUTTON_CHECKED`) 정밀 동기화
    - `k2ExpandLiveSpeedMenu`: 가상 리스트 인스턴스(`vInst.j`)의 메모이제이션 우회(`G = B`) 및 스냅샷 갱신(`vInst.A()`)
- [x] **2. 빌드 및 배포**
  - [x] Gradle 빌드: `.\gradlew.bat assembleDebug` 성공
  - [x] TV 기기 설치 및 실행: `adb install -r YT_TV_AC.apk` (`192.168.100.121:5555`)
- [x] **3. 실제 TV 실시간 검증 (사용자 입회 검증 완료)**
  - [x] 설정(톱니바퀴) -> 동영상 속도 진입 후 2.0x 아래로 스크롤하여 2.25x ~ 4x 항목 노출 및 스크롤 확인
  - [x] 메뉴에서 4x 선택 시 4.0x로 배속 변경 및 OSD 배지 노출 확인 (사용자 직접 확인 및 성공 승인)
  - [x] 메뉴에서 1x(일반) 복귀 및 리모컨 Ch+/Ch- 단계별 양방향 속도 제어 정상 동작 확인
- [x] **4. 문서화 및 버전 관리**
  - [x] `.agents/walkthrough_unlock_menu_speed_4x_and_vlist_scroll_20261017.md` 작성
  - [x] Git commit & push
