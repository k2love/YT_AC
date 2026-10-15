# 결과 리포트: GitHub 릴리즈 기반 인앱 자동 업데이트(OTA) 감지 및 설치

- **기능명**: GitHub 릴리즈 기반 인앱 자동 업데이트(OTA) 시스템
- **작성일**: 2026-10-16
- **저장소**: [k2love/YT_AC](https://github.com/k2love/YT_AC)

---

## 1. 구현 개요
GitHub 저장소([`k2love/YT_AC`](https://github.com/k2love/YT_AC))에 새로운 버전의 APK가 릴리즈될 때마다 Android TV 앱이 실행 시 최신 버전을 자동으로 감지하고, TV 리모컨으로 원클릭 다운로드 및 자동 설치를 진행할 수 있는 인앱 OTA(Over-The-Air) 업데이트 시스템을 완성했습니다.

---

## 2. 세부 구현 내역

### 2.1 인앱 업데이트 매니저 (`com.k2.youtubetv.update`)
1. **[`UpdateInfo.kt`](file:///E:/AI_Projects/##%20YouTube%20TV%20for%20Android%20Clone/app/src/main/java/com/k2/youtubetv/update/UpdateInfo.kt)**:
   - GitHub 릴리즈 정보(태그명, 제목, 릴리즈 노트, APK 다운로드 링크, 파일 크기) 데이터 모델
   - 시맨틱 버저닝(Semantic Versioning) 기반 비교 엔진 (`VersionComparator.isNewerVersion`)
     - `v1.0.1` vs `1.0.0` 등 접두사(`v`) 자동 정규화 및 각 자리수 정수 비교 처리
2. **[`AppUpdateManager.kt`](file:///E:/AI_Projects/##%20YouTube%20TV%20for%20Android%20Clone/app/src/main/java/com/k2/youtubetv/update/AppUpdateManager.kt)**:
   - **GitHub API 비동기 조회**: `https://api.github.com/repos/k2love/YT_AC/releases/latest` 백그라운드 호출
   - **TV 맞춤형 다이얼로그**: 리모컨 포커스가 기본적으로 '지금 업데이트' 버튼에 위치하도록 설계
   - **스트리밍 다운로드**: 다운로드 진행률(%) 및 용량(MB) 게이지를 실시간으로 표시하는 프로그레스 다이얼로그 제공
   - **자동 패키지 인스톨러 호출**: `FileProvider`를 통해 `content://` URI로 시스템 패키지 설치 화면 안전 호출

### 2.2 보안 및 권한 설정
1. **[`file_paths.xml`](file:///E:/AI_Projects/##%20YouTube%20TV%20for%20Android%20Clone/app/src/main/res/xml/file_paths.xml)**:
   - 앱 전용 다운로드 디렉토리(`getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)`)를 FileProvider에 매핑
2. **[`AndroidManifest.xml`](file:///E:/AI_Projects/##%20YouTube%20TV%20for%20Android%20Clone/app/src/main/AndroidManifest.xml)**:
   - `android.permission.REQUEST_INSTALL_PACKAGES` 권한 추가
   - `androidx.core.content.FileProvider` 등록 완료

### 2.3 수술적 최소 침습 연동
- **[`MainActivity.kt`](file:///E:/AI_Projects/##%20YouTube%20TV%20for%20Android%20Clone/app/src/main/java/com/k2/youtubetv/MainActivity.kt)**:
  - `onCreate` 내 코루틴에서 `appUpdateManager.checkForUpdates(isManualCheck = false)`를 단 한 줄로 연결하여 기존 재생/광고차단/키입력 로직에 영향을 전혀 주지 않도록 격리

### 2.4 GitHub Actions 자동 빌드 및 릴리즈 파이프라인 구축
- **[`.github/workflows/release.yml`](file:///E:/AI_Projects/##%20YouTube%20TV%20for%20Android%20Clone/.github/workflows/release.yml)**:
  - 사용자가 `v*` 태그(예: `git tag v1.0.1 && git push origin v1.0.1`)를 푸시하면 GitHub 클라우드에서 Ubuntu 환경으로 자동 빌드 후 `YT_TV_AC.apk`를 Release에 자동 첨부하도록 구성

---

## 3. 업데이트 동작 흐름 및 사용 방법

### 🚀 새 버전을 배포하는 방법 (2가지 중 편한 방법 선택)

#### [방법 A] GitHub 웹에서 직접 Release 등록 (수동 업로드)
1. `app/build.gradle.kts`에서 버전 업:
   - `versionCode = 2`
   - `versionName = "1.0.1"`
2. `./gradlew.bat assembleDebug` 실행하여 `YT_TV_AC.apk` 빌드
3. GitHub 저장소 [k2love/YT_AC Releases](https://github.com/k2love/YT_AC/releases) 페이지 접속
4. **Draft a new release** 클릭
   - Tag: `v1.0.1` 입력 (Target: `main`)
   - Release title: `v1.0.1 신규 업데이트`
   - Description: 변경 내역 작성
   - **Attach binaries**: 로컬의 `app/build/outputs/apk/debug/YT_TV_AC.apk`를 드래그 앤 드롭으로 첨부
5. **Publish release** 클릭!

#### [방법 B] Git 태그 푸시를 통한 자동 릴리즈 (GitHub Actions CI/CD)
1. `app/build.gradle.kts`의 `versionName` 수정 후 커밋
2. 터미널에서 태그 생성 및 푸시:
   ```powershell
   git tag v1.0.1
   git push origin v1.0.1
   ```
3. GitHub Actions가 자동으로 `YT_TV_AC.apk`를 빌드하여 Release를 자동 생성 및 파일 첨부 완료!

---

### 📺 안드로이드 TV에서의 업데이트 감지 및 설치 흐름
1. TV에서 `YT_TV_AC` 앱을 실행합니다.
2. 앱 실행 시 백그라운드에서 GitHub 최신 릴리즈 정보를 즉시 확인합니다.
3. 신규 버전이 존재하면 TV 화면 중앙에 다음과 같은 팝업이 표시됩니다:
   > **YouTube TV 신규 업데이트 알림**  
   > 새로운 버전(v1.0.1)이 출시되었습니다.  
   > [주요 변경사항] ...  
   > 지금 업데이트를 다운로드하여 설치하시겠습니까?  
   > **[지금 업데이트]** / **[나중에]**
4. 리모컨의 [확인] 버튼을 누르면 프로그레스 바와 함께 다운로드가 진행됩니다.
5. 다운로드가 완료되면 안드로이드 시스템 패키지 설치 화면이 자동으로 열려 업데이트 설치가 완료됩니다.

---

## 4. 빌드 검증 결과
- **빌드 상태**: `BUILD SUCCESSFUL in 1s`
- **산출물**: `E:\AI_Projects\## YouTube TV for Android Clone\app\build\outputs\apk\debug\YT_TV_AC.apk` (7,384,554 바이트, 약 7.38 MB)
- **한글 리터럴 무결성**: 인코딩 오차 없이 전수 정상 보존 확인 완료
