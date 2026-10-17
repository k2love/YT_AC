# 구현 계획서: 삼성 Tizen(.wgt) 및 LG webOS(.ipk) 멀티플랫폼 확장 및 깃허브 합병

- **문서 번호**: `implementation_plan_tizen_webos_expansion_20261017.md`
- **대상 프로젝트**: `## YouTube TV for Android Clone` (`YT_AC`)
- **작성 일시**: 2026-10-17

---

## 1. 개요 및 목표
안드로이드 TV 클론 앱에서 검증을 마친 초경량 고성능 YouTube TV 폴리필(`h5vcc_polyfill.js`) 및 리버스 엔지니어링 자산을 기반으로,
삼성 Tizen TV(`.wgt`) 및 LG webOS TV(`.ipk`)용 독립 웹 앱 템플릿을 구축하고, 즉시 패키징하여 실제 스마트 TV에 설치 가능한 산출물로 빌드한 뒤 현재 깃허브 리포지토리에 멀티플랫폼 모노레포 구조로 통합(합병)합니다.

---

## 2. 작업 내역 및 구조 설계

```
YT_AC (Repository Root)
├── app/                        <-- 기존 Android TV 네이티브 앱 (유지)
├── YT_TV_AC.apk                <-- Android TV 릴리즈 APK
├── platforms/
│   ├── tizen/                  <-- 삼성 Tizen TV 프로젝트
│   │   ├── config.xml          <-- Tizen 위젯 설정 및 도메인 권한
│   │   ├── index.html          <-- Tizen 스타트업 뷰 및 폴리필 선제 주입
│   │   ├── icon.png            <-- Tizen 앱 아이콘
│   │   ├── js/
│   │   │   ├── h5vcc_polyfill.js <-- 코발트 에뮬레이션 및 Zero-Ad v8
│   │   │   └── tizen_keys.js   <-- Tizen 리모컨 특수키/Back키(10009) 처리
│   │   └── build_tizen.py      <-- Tizen Studio 없이도 .wgt 즉시 패키징
│   │
│   └── webos/                  <-- LG webOS TV 프로젝트
│       ├── appinfo.json        <-- webOS 앱 메타데이터
│       ├── index.html          <-- webOS 스타트업 뷰 및 폴리필 선제 주입
│       ├── icon.png            <-- webOS 아이콘 (80x80)
│       ├── largeIcon.png       <-- webOS 런처 배너 (130x130)
│       ├── js/
│       │   ├── h5vcc_polyfill.js <-- 코발트 에뮬레이션 및 Zero-Ad v8
│       │   └── webos_keys.js   <-- webOS Back키(461)/매직리모컨 처리
│       └── build_webos.py      <-- webOS SDK 없이도 순수 Python으로 .ipk 즉시 패키징
│
└── scripts/
    └── build_all_platforms.py  <-- Android / Tizen / webOS 전 플랫폼 일괄 빌드 도구
```

---

## 3. 세부 구현 단계

1. **디렉토리 생성**:
   - `platforms/tizen/`, `platforms/webos/`, `scripts/` 디렉토리 구성.
2. **삼성 Tizen 템플릿 개발**:
   - `config.xml`: 전체화면 랜드스케이프, 4K 지원, 인터넷/키보드 권한, YouTube 도메인 화이트리스트.
   - `index.html`: 폴리필 주입 및 YouTube TV Leanback 로더.
   - `tizen_keys.js`: Tizen TV Input Device API 등록 및 리모컨 Back(`10009`) 핸들러.
   - `build_tizen.py`: 표준 W3C 위젯 사양에 맞춘 `.wgt` 압축 패키징 스크립트 작성 및 실행.
3. **LG webOS 템플릿 개발**:
   - `appinfo.json`: webOS 3.0~24+ 호환 메타데이터.
   - `index.html`: webOS 뷰포트 및 폴리필 선제 주입 로더.
   - `webos_keys.js`: webOS Back(`461`) 핸들러 및 포커스 헬퍼.
   - `build_webos.py`: 순수 Python 기반 `ar` + `tar.gz` (`debian-binary`, `control.tar.gz`, `data.tar.gz`) 정밀 패키징 스크립트 작성 및 `.ipk` 빌드.
4. **전체 패키지 빌드 및 검증**:
   - `YT_TV_AC_Tizen.wgt` 생성 검증
   - `YT_TV_AC_webOS.ipk` 생성 검증
5. **Git 커밋 및 GitHub 원격 푸시**:
   - 새 플랫폼 소스 및 빌드된 패키지들을 깃허브에 합병.
