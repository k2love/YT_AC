# 구현 계획서: 설정 화면 YouTube Premium 완전 제거 및 버전 1.0.1 상향

## 1. 개요 및 사용자 요구사항
- **요구사항 1**: 설정(톱니바퀴)으로 들어갔을 때 왼쪽 메뉴에서 'YouTube Premium 가입' 카드는 사라졌으나, 오른쪽 첫 화면(메인 화면)에 여전히 'YouTube Premium 가입' 배너/버튼이 노출되는 문제 해결.
- **요구사항 2**: '최신 앱 업데이트 확인' 실행 시 버전이 `v1.0.0`으로 고정되어 나오는 문제 해결 (빌드 시마다 버전 자동/수동 상향 반영, 이번 배포에서 `v1.0.1`로 갱신).

---

## 2. 근본 원인 분석
1. **오른쪽 'YouTube Premium 가입' 메인 화면 잔류 원인**:
   - YouTube TV의 InnerTube API(`/youtubei/v1/browse`)가 설정 메뉴를 반환할 때, 0번째 탭(`tabRenderer`)의 `content` 프로퍼티에 `settingActionRenderer`(YouTube Premium 가입 상세 화면)를 매핑해 둡니다.
   - 설정 화면이 최초로 로드되면 YouTube TV의 뷰 엔진은 기본값인 0번째 탭의 `content`를 우측 `ytlr-tv-surface-content-renderer`에 렌더링합니다.
   - 기존 패치에서는 좌측 DOM 리스트의 `ytlr-tab-renderer`에 대해서만 `display: none !important` 처리를 했기 때문에, 우측에 렌더링된 프리미엄 상세 화면(`ytlr-setting-action-renderer`)은 그대로 남아 사용자에게 노출되었습니다.
   - 또한 기존 탭 전환 조건이 `premiumTab.classList.contains('zylon-focus')`일 때만 발동하여, 사이드바에서 설정으로 막 진입한 시점에는 트리거되지 않았습니다.

2. **버전 번호 v1.0.0 고정 원인**:
   - `app/build.gradle.kts`의 `versionName`이 `"1.0.0"`으로 설정되어 있어, `BuildConfig.VERSION_NAME`을 읽는 `AppUpdateManager` 다이얼로그에서 계속 `v1.0.0`으로 출력되었습니다.

---

## 3. 상세 수정 계획 (수술적 정밀 최소 수정)

### 1) 앱 버전 번호 상향 (`app/build.gradle.kts`)
- `versionCode = 1` -> `versionCode = 2`
- `versionName = "1.0.0"` -> `versionName = "1.0.1"`

### 2) InnerTube 응답 계층에서 Premium 요소 원천 소멸 (`app/src/main/assets/h5vcc_polyfill.js`)
- `sanitizeAdsDirectly(obj)` 내에서 `item.tabRenderer` 또는 `item.settingActionRenderer`의 제목/텍스트에 `/Premium|프리미엄/i`가 매칭될 경우 해당 항목을 배열에서 즉시 삭제(`obj.splice(i, 1)`).
- 이렇게 하면 설정 데이터에서 0번째 탭이 'YouTube Premium'이 아닌 '구매 항목 및 멤버십'이 되며, 우측 화면 역시 '구매 항목 및 멤버십'의 상세 화면이 기본 렌더링됩니다.

### 3) DOM 레벨 우측 패널 프리미엄 제거 및 탭 동기화 보강 (`app/src/main/assets/h5vcc_polyfill.js`)
- `k2InjectSettingsUpdateCard()` 내에서:
  - 우측 `ytlr-tv-surface-content-renderer` 내의 `ytlr-setting-action-renderer` 중 텍스트에 Premium/프리미엄이 포함된 요소가 존재할 경우 즉시 `remove()` 또는 숨김 처리.
  - 설정 화면에 진입한 상태에서 첫 번째 유효 탭('구매 항목 및 멤버십')이 선택되지 않았을 경우, 첫 탭 버튼을 자동 클릭(`fBtn.click()`)하여 우측 패널을 항상 정상적인 첫 메뉴로 동기화.

---

## 4. 검증 계획
1. **빌드 검증**: `.\gradlew.bat assembleDebug` 성공 여부 확인.
2. **TV 배포**: `adb install -r YT_TV_AC.apk`로 실제 TV(`192.168.100.121:5555`)에 설치.
3. **실제 TV 화면 캡처 검증**:
   - 리모컨으로 설정(톱니바퀴) 진입 시 우측 메인 화면이 'YouTube Premium'이 아닌 '구매 항목 및 멤버십'으로 깨끗하게 노출되는지 캡처 확인.
   - '최신 앱 업데이트 확인' 실행 시 다이얼로그에 `v1.0.1`로 정상 표시되는지 캡처 확인.
4. **결과 문서화 및 Git 푸시**:
   - `walkthrough_settings_premium_purge_and_version_bump_20261016.md` 작성 및 원격 저장소 푸시.
