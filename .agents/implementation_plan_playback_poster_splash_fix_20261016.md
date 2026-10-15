# YouTube TV 클린룸: 재생 정상화, 비디오 포스터 제거 및 스플래시 투명화 계획서

## 1. 개요 및 사용자 피드백 분석
- **보고된 문제**:
  1. 영상 재생이 안 됨.
  2. 영상 재생 시작 시 검은 바탕에 하얀 플레이 버튼이 여전히 뜸.
  3. 앱 시작 시 유튜브 로고 크기는 줄었으나 뒷배경이 투명이 아님.
- **근본 원인 규명**:
  1. `TVWebViewClient.kt`의 `isVideoAdStream`이 본 영상 스트림(`googlevideo.com/videoplayback?...ctier=...`)을 광고로 오인하여 204 No Content를 반환함 -> 비디오 버퍼를 채우지 못해 재생 불가.
  2. `TVWebChromeClient.kt`에 `getDefaultVideoPoster()`가 구현되지 않아 안드로이드 WebView 기본 비디오 포스터(검은 바탕 + 흰색 재생 버튼 아이콘)가 비디오 로드 대기 시 노출됨.
  3. `#loader`에 `#0f0f0f` / `#282828` 불투명 배경색이 지정되어 있어 로고 뒤 사각형 영역이 불투명하게 표시됨 -> 오리지널은 `transparent` 투명 배경에 로고만 노출.

## 2. 해결 구현 계획
1. **`TVWebViewClient.kt` 비디오 스트림 가로채기 제거**:
   - `isVideoAdStream` 제거: `googlevideo.com/videoplayback`은 절대 204로 막지 않고 정상 통과시킴.
   - 광고 차단은 `/youtubei/v1/player`의 `adPlacements = []`, `adSlots = []`, `playerAds = null`과 트래커 차단으로 무결하게 유지.
2. **`TVWebChromeClient.kt` 기본 비디오 포스터 투명화**:
   - `override fun getDefaultVideoPoster(): Bitmap?` 추가하여 1x1 투명 비트맵 반환 -> 검은 바탕 흰색 플레이 버튼 영구 소멸.
3. **`NativeAdSanitizer.kt` & `h5vcc_polyfill.js` 스플래시 투명 배경 적용**:
   - `#loader, .splash-screen-loader`의 `background-color: transparent !important;` 적용.
4. **빌드 및 실기기 검증**:
   - `gradlew.bat assembleDebug` 성공 확인.
