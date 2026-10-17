# Release Notes: v1.0.3

## 릴리즈 개요
- **버전**: `1.0.3` (versionCode: 4)
- **APK 파일**: `YT_TV_AC.apk` (5,204,695 bytes)
- **대상 기기**: Android TV (`com.k2.youtubetv`)

---

## 주요 변경 및 개선 사항

### 1. 플레이어 HUD 및 컨트롤 문자 라벨 완전 투명화
- 동영상 재생 중 리모컨 아래 방향(DOWN) 버튼을 눌러 HUD를 열고 컨트롤 버튼(채널, 이전, 다음, 좋아요 수, 싫어요, 댓글, 질문하기, 저장, Super Thanks, 자막, 설정)을 좌우로 이동할 때 나타나는 툴팁 문자 설명의 짙은 회색/검은색 박스 배경을 완전 제거.
- `.A71IFd`, `.TamOWc`, `[class*="A71IFd"]`, `[class*="TamOWc"]` 및 저사양 fallback 클래스(`.E7WdFf`, `.QOsyFf`, `.ApXCd`, `.KQT3Oe`, `.CO0KFd`, `.dsDLs`, `.pPJooc`)에 대해 `background: transparent !important;` 및 `border: none !important; box-shadow: none !important; color: #ffffff !important;` 영구 적용.

### 2. TV UI 상단 200px 밀림(Shift) 현상 원천 차단
- `TVWebView.kt`: `scrollTo(x, y)` 오버라이드로 `(0, 0)` 완전 고정, `overScrollMode = OVER_SCROLL_NEVER`, 스크롤바 비활성화로 Android 프레임워크에 의한 네이티브 뷰포트 밀림 방지.
- `AndroidManifest.xml`: `android:windowSoftInputMode="adjustNothing|stateAlwaysHidden"` 지정으로 텍스트 입력 및 포커스 이동 시 윈도우 패닝 차단.
- `h5vcc_polyfill.js`: 불필요한 `purgeQualityRoot()` 및 전역 MutationObserver를 제거하여 YouTube TV 순정 TV 레이아웃 안정성 유지.

### 3. 디스크 캐시 무효화 및 새 CSS 컴파일 보장
- `TVWebViewClient`의 `PATCH_VERSION`을 `8`로 상향하여 디스크에 캐시된 구형 CSS/JS를 즉각 무효화하고 최신 패치가 즉시 반영되도록 구현.
