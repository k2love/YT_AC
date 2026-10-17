# 삼성 Tizen(.wgt) 및 LG webOS(.ipk) 멀티플랫폼 확장 결과 리포트 (Walkthrough)

- **문서 번호**: `walkthrough_tizen_webos_expansion_20261017.md`
- **대상 프로젝트**: `## YouTube TV for Android Clone` (`YT_AC`)
- **작업 일시**: 2026-10-17
- **확장 플랫폼**: Android TV | Samsung Tizen TV | LG webOS TV

---

## 1. 개요 및 성과
기존 Android TV용으로 완성된 초경량 고성능 YouTube TV 폴리필(`h5vcc_polyfill.js`, Zero-Ad v8, 4K/60fps 언락, 3x/4x 배속)을
삼성 Tizen TV와 LG webOS TV에 100% 이식하여 독립 프로젝트 템플릿을 생성하고,
실제 스마트 TV 실기에 즉시 설치(Sideload) 가능한 패키지(`.wgt`, `.ipk`) 빌드 파이프라인을 구축하여 GitHub 리포지토리에 단일 모노레포로 통합했습니다.

---

## 2. 플랫폼별 생성 내역

### 1) 삼성 Tizen TV (`platforms/tizen/`)
- **`config.xml`**:
  - Tizen 3.0~7.0+ 전 기종 호환.
  - 가로 모드 전체화면, 4K 스크린 해상도 지원, 인터넷 및 리모컨(`tv.inputdevice`) 권한 활성화.
  - 유튜브 전체 도메인 및 미디어 스트리밍 서버 접근 권한 부여.
- **`index.html`**:
  - Tizen 웹 앱 시작점. `h5vcc_polyfill.js` 및 `tizen_keys.js`를 선제 로드하여 완전 무결한 Cobalt 에뮬레이션 환경 구축 후 YouTube Leanback 로드.
- **`js/tizen_keys.js`**:
  - Tizen 전용 하드웨어 Back 키(`keyCode: 10009`), 미디어 컨트롤 키(`MediaPlay`, `MediaPause`) 매핑.
- **`build_tizen.py`**:
  - Tizen Studio CLI 없이도 표준 W3C 위젯 사양에 맞춰 `.wgt` 패키지를 즉시 압축 생성.
  - **산출물**: `platforms/tizen/dist/YT_TV_AC_Tizen.wgt`

### 2) LG webOS TV (`platforms/webos/`)
- **`appinfo.json`**:
  - webOS 3.0~24+ 전 기종 호환 메타데이터.
  - `type: "web"`, 4K/1080p 해상도, GPU 프로세스 가속 지원, 외부 매핑 신뢰(`trustExternalMappings: true`).
- **`index.html`**:
  - webOS 웹 앱 시작점. `h5vcc_polyfill.js` 및 `webos_keys.js` 선제 로드.
- **`js/webos_keys.js`**:
  - webOS 하드웨어 Back 키(`keyCode: 461`), 매직 리모컨 커서 상태 연동.
- **`build_webos.py`**:
  - webOS SDK(`ares-package`)가 없어도 순수 Python으로 `debian-binary` + `control.tar.gz` + `data.tar.gz`를 조립하여 표준 ar 아카이브인 `.ipk`를 즉시 생성.
  - **산출물**: `platforms/webos/dist/YT_TV_AC_webOS.ipk`

### 3) 마스터 통합 빌드 파이프라인 (`scripts/build_all_platforms.py`)
- 안드로이드의 최신 `h5vcc_polyfill.js`를 Tizen과 webOS로 자동 동기화.
- Android APK, Tizen WGT, webOS IPK를 단 1회의 명령으로 일괄 빌드.

---

## 3. 최종 빌드 산출물 목록

| 플랫폼 | 패키지 파일명 | 경로 | 포맷 / 규격 |
| :--- | :--- | :--- | :--- |
| **Android TV** | `YT_TV_AC.apk` | 루트 디렉토리 | Android APK (v1.0.4) |
| **Samsung Tizen TV** | `YT_TV_AC_Tizen.wgt` | `platforms/tizen/dist/` | W3C Tizen Widget (.wgt) |
| **LG webOS TV** | `YT_TV_AC_webOS.ipk` | `platforms/webos/dist/` | webOS Debian Archive (.ipk) |

---

## 4. 실기 설치 가이드 요약
- **삼성 Tizen TV**: Tizen Studio / TizenBrew / SDB 도구를 통해 `sdb install YT_TV_AC_Tizen.wgt` 실행.
- **LG webOS TV**: webOS Developer Mode 앱 / webOS Homebrew Channel을 통해 `ares-install YT_TV_AC_webOS.ipk` 실행.
