# Walkthrough: 루트 APK 커밋 기반 원클릭 자동 업데이트 시스템 구축

GitHub Releases(릴리즈 태그/에셋)를 거치지 않고도, 프로젝트 루트에 위치한 `YT_TV_AC.apk` 파일을 `git commit & push`하는 것만으로 안드로이드 TV 앱이 파일의 커밋 시각(ISO 8601)과 커밋 SHA를 감지하여 바로 다운로드 및 설치하도록 기능을 전환 완료했습니다.

---

## 1. 구현 내용 요약

### 1) `.gitignore` 설정 수정
- 기존의 모든 `*.apk` 무조건 무시 정책에서 루트 파일 `!/YT_TV_AC.apk`를 예외 등록하여 깃(Git) 추적을 허용했습니다.
- 이제 빌드된 최신 `YT_TV_AC.apk`를 프로젝트 루트에 두고 푸시하면 원격 저장소에 즉시 반영됩니다.

### 2) `AppUpdateManager.kt` 엔진 전환
- **1순위 감지 (GitHub Commits API)**:
  - 엔드포인트: `https://api.github.com/repos/k2love/YT_AC/commits?path=YT_TV_AC.apk&sha=main&page=1&per_page=1`
  - GitHub에 루트 `YT_TV_AC.apk`가 푸시된 커밋 시각(`commit.committer.date`)과 로컬 앱 설치/업데이트 시각(`packageInfo.lastUpdateTime`)을 밀리초 단위로 비교합니다.
  - 리모트 커밋 시간이 로컬 설치 시간보다 1분 이상 최신이거나 저장된 커밋 SHA와 다르면 신규 업데이트로 판단합니다.
- **스트리밍 직접 다운로드**:
  - 엔드포인트: `https://raw.githubusercontent.com/k2love/YT_AC/main/YT_TV_AC.apk`
  - 릴리즈 에셋 링크 없이 GitHub raw 저장소 주소에서 직접 바이트 스트리밍을 받아 내부 캐시 디렉터리로 다운로드하고 `FileProvider`를 통해 시스템 패키지 인스톨러를 자동 호출합니다.
- **2순위 감지 (Releases API 보조 지원)**:
  - 루트 커밋 기록이 없거나 릴리즈 태그가 발행되었을 경우에도 동작하도록 하이브리드 파이프라인 유지.

---

## 2. 변경 파일 목록

| 파일 경로 | 작업 내용 |
|---|---|
| `.gitignore` | `!/YT_TV_AC.apk` 예외 추가로 루트 APK 추적 허용 |
| `YT_TV_AC.apk` | 최신 빌드 산출물 복사 및 원격 배포 준비 |
| `app/src/main/java/com/k2/youtubetv/update/AppUpdateManager.kt` | GitHub Commits API 파싱, 시각/SHA 비교, raw 다운로드 로직 이식 |
| `.agents/implementation_plan_root_apk_commit_updater_20261016.md` | 구현 계획서 작성 |
| `.agents/task.md` | 작업 진행 현황 갱신 |

---

## 3. 검증 결과

1. **Gradle 빌드 검증**:
   - `.\gradlew.bat assembleDebug` 실행 결과: `BUILD SUCCESSFUL in 1s`
   - APK 산출물 정상 생성: `app/build/outputs/apk/debug/YT_TV_AC.apk`
2. **루트 APK 동기화**:
   - `YT_TV_AC.apk` 파일 갱신 완료 (`7,384,554 bytes`)
3. **인코딩 및 한글 리터럴 점검**:
   - UI 다이얼로그 및 메시지 한국어 정상 출력 검증 완료.
