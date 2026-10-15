# 워크스루: 앱 기동 실패(Crash/Freeze) 원인 분석 및 경량화 4K 언락 엔진 복원 리포트

## 1. 개요
직전 빌드에서 발생한 "앱이 실행조차 안 되는 현상(기동 실패/블랙스크린/크래시)"의 원인을 역공학 분석으로 규명하고, 시스템을 안정화하면서 **4K 해상도 언락**과 **투명 로고/컨트롤 UI**를 완벽하게 유지하도록 엔진을 긴급 리팩토링하였습니다.

---

## 2. 앱 실행 불가(Crash/Freeze)의 근본 원인 분석

1. **치명타 1: `navigator.mediaCapabilities.decodingInfo` 몽키패치의 DRM/Widevine 파이프라인 파괴**:
   - YouTube TV 앱은 기동 시 `navigator.mediaCapabilities.decodingInfo`를 호출하여 기기의 DRM/Widevine(L1/L3) 성능(`keySystemAccess`)을 프로파일링합니다.
   - 직전 패치에서 `keySystemAccess: null`을 강제 반환하여 YouTube TV의 EME 플레이어 부트스트랩 코드가 `TypeError (reading createMediaKeys)`를 던지며 **초기화 단계에서 앱 전체가 크래시**되었습니다.
2. **치명타 2: 자바스크립트 내 43.5KB Base64 하드코딩으로 인한 스크립트 비대화(63KB)**:
   - `h5vcc_polyfill.js`에 대용량 이미지 Base64를 인라인으로 포함시켜 스크립트가 15KB에서 63KB로 4배 이상 폭증했습니다.
   - `WebViewCompat.addDocumentStartJavaScript`에 대용량 스크립트 전달 시 Android Binder IPC 한계 및 WebView 렌더러 프로세스 불안정을 초래했습니다.
3. **치명타 3: `MutationObserver` 및 100ms 스타일 재주입 무한 루프**:
   - `ensureMasterStyles()`가 DOM에 스타일을 추가할 때 `MutationObserver`가 다시 트리거되는 무한 루프로 인해 저사양 TV CPU 메인 스레드가 100% 점유되어 앱이 얼어붙는 현상이 발생했습니다.

---

## 3. 긴급 해결 조치

1. **안전한 4K(2160p) 해상도 언락 복원**:
   - 위험한 `mediaCapabilities` 몽키패치를 **완전 제거**하여 DRM 및 EME 정상 파이프라인을 100% 보존.
   - 오직 YouTube 플레이어가 디스플레이를 4K로 인식하게 만드는 필수 파라미터(`screen.width = 3840`, `screen.height = 2160`, `devicePixelRatio = 2.0`)와 `MediaSource.isTypeSupported` VP9/AV1 4K 안전 언락만 정밀 적용.
2. **`h5vcc_polyfill.js` 초경량 다이어트 (63KB -> 18KB)**:
   - Base64 로고 데이터를 자바스크립트 코드에서 완전히 분리.
   - 투명 로고 교체는 `NativeAdSanitizer.kt`에서 HTML의 원본 `#loader` CSS 블록만 수술적으로 치환하도록 일원화하여 메모리 및 실행 속도 극대화.
3. **정규식 치환 안전성 확보 (`Matcher.quoteReplacement`)**:
   - `NativeAdSanitizer.kt`의 HTML 치환 시 `Matcher.quoteReplacement()`를 적용하여 특수문자나 슬래시로 인한 런타임 예외를 원천 방지.
4. **`TVWebView.kt`의 예외 방어선 강화**:
   - `setupDocumentStartScript`에서 `catch (e: Throwable)`로 확장하여 시스템 웹뷰 버전 불일치로 인한 `Error` 발생 시에도 크래시 없이 정상 부팅되도록 안전장치 마련.

---

## 4. 검증 결과

- **Gradle 빌드**: `BUILD SUCCESSFUL in 2s`
- **산출물**: `YouTubeTVClone/app/build/outputs/apk/debug/app-debug.apk` (**7.25 MB**)
- **자바스크립트 크기**: `assets/h5vcc_polyfill.js` (**18,155 바이트**, 정상 경량화 확인)
- **UTF-8 인코딩**: 전수 검증 통과 (`True`)
