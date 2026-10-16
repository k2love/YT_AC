# 작업 보드: 리모컨 뒤로가기(Back) 동작 불능 현상 원인 규명 및 근본 해결

## 1. 개요 및 사용자 요구사항
- **요구사항**: "종종 뒤로가기 버튼이 안 먹어."
- **증상 및 분석 결과**:
  1. **영상 시청 중 뒤로가기 불능**: `document.body`에 항상 존재하는 `app-quality-root` 클래스로 인해 `BODY` 태그가 팝업/메뉴 오버레이로 오판됨. 이로 인해 `BODY` 내의 `aria-label="0초 뒤로 건너뜁니다..."` 재생바(Seek bar)를 닫기 버튼으로 오인하여 클릭하거나 `NEEDS_ESCAPE:menu`를 반환하여 영상이 닫히지 않고 먹통이 됨.
  2. **홈 화면 외 하위 페이지(검색, 설정, 채널 등)에서 뒤로가기 불능**: 비디오나 팝업이 아닌 상태는 무조건 `ROOT_HOME`으로 취급하여 웹뷰에 아무런 뒤로가기/Escape 키를 전달하지 않고 앱 종료 토스트만 띄움.

## 2. 작업 목록
- [x] 1. `implementation_plan_back_key_fix_20261016.md` 계획서 작성
- [x] 2. `TVRemoteKeyHandler.kt` 수술적 정밀 수정:
  - 오버레이 탐색 대상에서 `BODY` 및 `HTML` 제외 (`node === document.body || node.tagName === 'BODY'`)
  - `closer` 검색 시 탐색바/시크바("건너뜁니다", "초 뒤", "seek" 등) 제외 및 엄격한 닫기/뒤로 버튼 매칭
  - 홈 화면 판별 로직 정밀화: `hash`가 `#/`, `""`, `#/browse`(루트)일 때만 `ROOT_HOME` 처리, 그 외(설정, 검색, 채널, 재생목록 등)는 `NEEDS_ESCAPE:subpage`로 이전 화면 복귀 처리
  - 영상 시청 중 Escape 처리 및 상태 전이 안정화
- [x] 3. Gradle 빌드 (`gradlew assembleDebug`)
- [x] 4. TV 기기(`192.168.100.121:5555`)에 APK 설치 및 앱 테스트
- [x] 5. 실제 TV에서 뒤로가기 시나리오별 검증 및 화면 캡처:
  - 영상 시청 중 뒤로가기 -> 홈/이전 화면 정상 복귀 (`tv_screen_after_back.png`)
  - 서브 카테고리/설정 화면에서 뒤로가기 -> 홈 화면 정상 복귀
  - 홈 화면에서 뒤로가기 1회 -> 토스트 노출, 2회 -> 앱 정상 종료
- [x] 6. `walkthrough_back_key_fix_20261016.md` 작성
- [x] 7. GitHub 원격 저장소 커밋 및 푸시
