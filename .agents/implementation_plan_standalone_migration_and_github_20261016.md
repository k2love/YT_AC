# 구현 계획서: YouTube TV Clone 프로젝트 독립 이관, APK 파일명 변경(YT_TV_AC.apk) 및 GitHub 배포 준비

## 1. 개요
현재 `E:\AI_Projects\## REA (Reverse Engineering Anything)\YouTubeTVClone`에 종속되어 있는 앱을 `E:\AI_Projects\## YouTube TV for Android Clone`이라는 완전히 독립된 프로젝트로 분리 및 이관하고, 패키징 산출물 파일명을 `YT_TV_AC.apk`로 변경하며, 오픈소스/GitHub 공개를 위한 환경(저장소 초기화, `.gitignore`, 완성도 높은 `README.md`, 초기 커밋)을 완벽하게 구축합니다.

---

## 2. 세부 실행 계획

### A. 디렉토리 구조 설계 및 이관
- **신규 독립 경로**: `E:\AI_Projects\## YouTube TV for Android Clone`
- **복사/이관 대상**:
  1. 안드로이드 프로젝트 전체:
     - `app/` (소스 코드, 레이아웃, assets, 매니페스트)
     - `gradle/` (wrapper jar, properties)
     - `build.gradle.kts`, `settings.gradle.kts`, `gradle.properties`, `local.properties`
     - `gradlew`, `gradlew.bat`
  2. 문서 및 분석 데이터:
     - `.agents/` 디렉토리 (역공학 분석 스크립트, 투명 로고 원본, 인수인계 문서, 워크스루 등)
- 빌드 캐시(`.gradle`, `build`, `app/build`)는 깨끗한 상태로 재구축하기 위해 이관 시 제외하거나 빌드 시 자동 생성되도록 함.

### B. APK 출력 파일명 변경 (`YT_TV_AC.apk`)
- `app/build.gradle.kts`에 `applicationVariants` 후처리 블록 추가:
  ```kotlin
  android {
      ...
      applicationVariants.all {
          outputs.all {
              val output = this as? com.android.build.gradle.internal.api.BaseVariantOutputImpl
              output?.outputFileName = "YT_TV_AC.apk"
          }
      }
  }
  ```
- 빌드 후 `app/build/outputs/apk/debug/YT_TV_AC.apk`로 생성되는지 확인.

### C. GitHub 배포 준비
1. **`.gitignore` 파일 생성**:
   - `.gradle/`, `build/`, `app/build/`
   - `local.properties` (개인 SDK 경로 보호)
   - `.idea/`, `*.iml`, `captures/`
   - `.DS_Store`, `Thumbs.db`
2. **`README.md` 작성**:
   - 프로젝트명: **YouTube TV for Android Clone (YT_TV_AC)**
   - 특징:
     - 순정 YouTube for Android TV (v7.28.300 Cobalt 24) 100% 호환 UI/UX
     - 완벽한 제로-애드 (대문 머스트헤드, 인피드, 1~2초 사후 광고, 백그라운드 광고음 0% 차단)
     - 4K(2160p) 및 8K(4320p) 고화질 완벽 언락 (뷰포트/칩셋 필터 무제한 패스스루)
     - 완전 투명 컨트롤/메뉴 및 순정 느낌의 텍스트 섀도우
     - 스마트 TV 리모컨 뒤로가기/미디어 제어 완벽 지원
   - 빌드 및 설치 가이드 (Gradle, ADB)
   - 아키텍처 다이어그램 및 주요 모듈 설명
3. **Git 저장소 초기화**:
   - `git init`
   - `git branch -M main`
   - `git add .`
   - `git commit -m "feat: Initial commit for YouTube TV for Android Clone (YT_TV_AC)"`

---

## 3. 검증 계획
1. 새 디렉토리(`E:\AI_Projects\## YouTube TV for Android Clone`)에서 `.\gradlew.bat assembleDebug` 실행.
2. `app/build/outputs/apk/debug/YT_TV_AC.apk` 파일 존재 및 크기 검증.
3. `git status` 및 `git log` 정상 여부 확인.
4. 결과 리포트 작성.
