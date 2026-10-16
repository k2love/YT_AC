# 구현 계획서: 설정 메뉴 업데이트/버전 탭 분리 및 YouTube Premium 가입 항목 숨김

## 1. 개요
사용자 요구사항:
1. YouTube TV [설정] 메뉴의 최하단에 위치한 `최신 앱 업데이트 확인` 탭과 `앱 버전` 탭이 리모컨 조작 시 동시에 하이라이트(선택)되는 현상을 완벽하게 분리.
2. [설정] 메뉴의 최상단에 있는 `YouTube Premium 가입` 항목을 완전히 숨김(제거).

## 2. 근본 원인 분석
1. **동시 선택 및 하이라이트 잔류 원인**:
   - `versionTab.cloneNode(true)` 복제 시점에 `versionTab`에 부여되어 있던 포커스 클래스(`V0Tdtb`, `qzhmA`, `zylon-focus`, 내부 버튼의 `BZ345e`, `zylon-focus` 등)가 그대로 복제되어 `myTab`에 영구 고착됨.
   - 복제된 노드는 idom(Incremental DOM)의 관리 대상이 아니므로 포커스가 다른 곳으로 이동해도 하얗게 빛나는 스타일 클래스가 자동 제거되지 않음.
   - 이로 인해 `versionTab`으로 이동하면 두 항목 모두 하얗게 활성화되어 한 덩어리로 선택된 것처럼 보임.
   - 또한 우측 상세 화면이 `앱 버전` 패널을 그대로 공유하여 시각적으로 같은 메뉴처럼 인식됨.
2. **YouTube Premium 가입 잔류 원인**:
   - YouTube TV 순정 설정 메뉴의 인덱스 0번 탭으로 렌더링되며, 기존 필터링 규칙에 포함되지 않았음.

## 3. 정밀 해결 방안 (Surgical Fix)
### A. YouTube Premium 가입 항목 숨김
- `k2InjectSettingsUpdateCard()` 및 MutationObserver 주기 실행 시:
  - 전체 `ytlr-tab-renderer` 중 `innerText`에 `/Premium|프리미엄/i` 정규식에 매칭되는 요소를 탐색.
  - 해당 요소에 `display: none !important`, `aria-hidden: true`, `hybridnavfocusable: false`를 부여하여 화면과 포커스 트리에서 완전 배제.

### B. `최신 앱 업데이트 확인`과 `앱 버전` 완전 분리
1. **순수 비활성(Unselected) 상태로 초기화**:
   - 복제 시 `myTab` 및 하위 요소(`ytlr-button`, `ytlr-avatar-lockup`)에서 포커스 관련 클래스 전면 제거:
     - 탭 렌더러: `V0Tdtb`, `qzhmA`, `zylon-focus` 제거 -> 순수 `JqwODe`만 유지.
     - 버튼: `BZ345e`, `zylon-focus` 제거 -> `iM3bAd pAenK kOYqWe EZJGFd` 복원.
     - 락업: `dalgG` 제거 -> `yZD8Ze HRe9Le bWcqr` 복원.
   - 고유 식별자 부여:
     - `myTab.id = 'yt-ac-settings-update-banner'`
     - `aria-labelledby`, `aria-controls` 등 버전 관련 속성 고유화/제거.
2. **포커스 상태 격리 및 상호 배타성 보장**:
   - `myTab`의 `focusin` / `focusout` 이벤트 리스너:
     - `focusin`: `myTab`에만 포커스 클래스 부여, `versionTab`에서는 포커스 클래스 즉시 박탈.
     - `focusout`: `myTab`의 포커스 클래스 제거하여 비활성 상태로 복귀.
   - `versionTab`의 `focusin` 이벤트 리스너:
     - `versionTab`에 포커스가 오면 `myTab`의 포커스 클래스 즉시 제거.
3. **우측 상세 패널(Detail Panel) 독립 연동**:
   - `myTab` 포커스 시 우측 상세 화면(`YTLR-TV-SURFACE-CONTENT-RENDERER` 영역)에 전용 업데이트 안내 패널(커스텀 DOM)을 표시하고 기존 버전 패널을 일시 숨김.
   - `myTab` 포커스 이탈(`focusout`) 또는 타 메뉴 선택 시 원래 상세 패널 복구.
4. **리모컨 D-Pad 탐색 지원**:
   - `myTab`에서 `ArrowUp` (keyCode 38 / 19): 바로 위 탭(`개인정보 보호 및 약관`)으로 포커스 이동.
   - `myTab`에서 `ArrowDown` (keyCode 40 / 20): 바로 아래 `앱 버전` 탭으로 포커스 이동.
   - `myTab`에서 `Enter` (keyCode 13 / 23): `window.YT_TV_APP.checkAppUpdate()` 즉시 실행.

## 4. 검증 계획
1. `gradlew assembleDebug` 빌드 검증
2. TV 기기(`192.168.100.121:5555`)에 설치 및 앱 실행
3. 설정 화면 진입 후:
   - 최상단 `YouTube Premium 가입`이 사라졌는지 화면 캡처 확인.
   - `최신 앱 업데이트 확인`으로 포커스 이동 시 단독 하이라이트 및 전용 패널 노출 확인.
   - `앱 버전`으로 포커스 이동 시 단독 하이라이트 및 버전 정보 노출 확인.
   - `최신 앱 업데이트 확인`에서 OK 키 입력 시 업데이트 다이얼로그 정상 팝업 확인.
