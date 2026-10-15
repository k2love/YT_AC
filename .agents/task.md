# 작업 보드: GitHub 릴리즈 기반 인앱 자동 업데이트(OTA) 감지 및 설치 구현

- [x] 1. 계획 수립 및 사전 검증 <!-- id: 0 -->
    - [x] 빌드 무결성 사전 확인
    - [x] GitHub Releases API 및 Android TV 다운로드/설치 사양 설계
    - [x] 구현 계획서(`.agents/implementation_plan_github_ota_update_20261016.md`) 작성
- [x] 2. 권한 및 FileProvider 환경 설정 <!-- id: 1 -->
    - [x] `res/xml/file_paths.xml` 생성 (APK 안전 공유용)
    - [x] `AndroidManifest.xml`에 `REQUEST_INSTALL_PACKAGES` 및 `FileProvider` 등록
- [x] 3. OTA 업데이트 매니저 모듈 구현 <!-- id: 2 -->
    - [x] `com.k2.youtubetv.update.UpdateInfo` 데이터 클래스 및 버전 비교 유틸 작성
    - [x] `com.k2.youtubetv.update.AppUpdateManager` 구현 (GitHub API 비동기 조회, TV 최적화 다이얼로그, OkHttp 스트리밍 다운로드 및 패키지 인스톨러 연동)
- [x] 4. MainActivity 수술적 연동 <!-- id: 3 -->
    - [x] `MainActivity.onCreate` 내 비침습적 백그라운드 업데이트 확인 로직 연결
- [x] 5. 빌드 검증 및 릴리즈 가이드 작성 <!-- id: 4 -->
    - [x] `.\gradlew.bat assembleDebug` 빌드 검증 및 `YT_TV_AC.apk` (7.38 MB) 생성 확인
    - [x] GitHub Actions 자동 릴리즈 워크플로우(`.github/workflows/release.yml`) 추가
    - [x] 결과 리포트(`.agents/walkthrough_github_ota_update_20261016.md`) 작성 및 사용자 보고
