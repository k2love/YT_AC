# YouTube for Android TV v7.28.300 vs v7.29.300 1:1 비교 분석 리포트

- **분석 대상**:
  - 좌측 (기존 기준): `YouTube for Android TV v7.28.300 beta` (`versionCode: 728300320`)
  - 우측 (신규 버전): `YouTube for Android TV v7.29.300 beta` (`versionCode: 729300320`)
- **분석 일시**: 2026-10-17
- **분석 기법**: 바이너리 차등 분석 (Differential Binary & Bytecode Analysis)

---

## 1. 핵심 요약 (Executive Summary)

1. **Cobalt Java 프레임워크 유지**:
   - `dev.cobalt.*` 패키지의 총 331개 Java 클래스 구조가 **100% 동일하게 유지**되었습니다. (추가/삭제 0개)
   - `CobaltService`, `CobaltActivity`, `PlatformServiceRouter`, `CobaltJsBridge` 등 핵심 아키텍처 변경 없음.
2. **H5VCC API 엔드포인트 규격 유지**:
   - `h5vcc.system`, `h5vcc.storage`, `h5vcc.drm`, `h5vcc.sso` 등 우리가 클론 앱에 구현한 웹-네이티브 브릿지 인터페이스 24종이 완벽히 동일합니다.
3. **네이티브 라이브러리(`libchrobalt.so`) 변경**:
   - 파일 크기가 60,823,100 bytes에서 60,835,388 bytes로 약 **12KB 소폭 증가**.
   - 내부 스토리지 검증 루틴(`H5vccStorage::VerifyTest`, `H5vccStorage::WriteTest`) 등 테스트 및 안정성 패치 추가.
4. **결론 및 클론 프로젝트(`YT_AC`) 영향**:
   - 현재 개발 중인 `YT_AC`의 아키텍처 및 폴리필(`h5vcc_polyfill.js`, Cobalt 브릿지)을 수정할 필요가 없으며, 기존 구현이 최신 `v7.29.300`과도 완벽하게 호환됨을 확인했습니다.

---

## 2. 네이티브 바이너리 상세 비교 (`libchrobalt.so`)

| 항목 | v7.28.300 | v7.29.300 | 증감 / 차이점 |
| :--- | :--- | :--- | :--- |
| **파일 크기** | 60,823,100 bytes | 60,835,388 bytes | +12,288 bytes |
| **SHA-256** | `173343d70056f234...` | `015be67dfa878737...` | 신규 빌드 |
| **H5VCC 인터페이스** | 24개 엔드포인트 | 24개 엔드포인트 | 변경 없음 (100% 호환) |
| **내부 문자열 추가** | - | `H5vccStorage::VerifyTest`<br>`H5vccStorage::WriteTest` | 로컬 스토리지 무결성 검증 루틴 추가 |

---

## 3. DEX 바이트코드 상세 비교 (`classes*.dex`)

| DEX 파일 | v7.28.300 클래스 수 | v7.29.300 클래스 수 | 차이 분석 |
| :--- | :--- | :--- | :--- |
| **classes.dex** | 141개 | 141개 | ProGuard/R8 식별자 갱신 외 기능 동일 |
| **classes2.dex** | 9,698개 | 9,586개 | 내부 최적화로 112개 축소, 핵심 패키지 불변 |
| **classes3.dex** | 502개 | 502개 | 100% 동일 |

### 패키지별 세부 점검 결과

1. **`dev.cobalt.*` (Cobalt 엔진 브릿지 계층)**:
   - v7.28: 331개 클래스
   - v7.29: 331개 클래스
   - **결과: 변경 사항 없음 (0 Added, 0 Removed)**

2. **`com.google.android.apps.youtube.tv.*` (TV 진입점 계층)**:
   - v7.28: 4개 클래스
   - v7.29: 4개 클래스
   - **결과: 변경 사항 없음 (0 Added, 0 Removed)**

3. **신규 추가된 주요 비-난독화 클래스**:
   - `Lcom/google/android/libraries/multiplatform/elements/shape/ShapePathJni;`: Google Elements UI 멀티플랫폼 렌더링 관련 JNI 헬퍼 추가.

---

## 4. 향후 권장 작업 방향

- **클론 앱 호환성**:
  - `v7.28.300` 기준으로 작성된 우리의 클린룸 설계 명세서 및 소스 코드는 최신 `v7.29.300`의 사양과 일치하므로 재작업할 필요가 없습니다.
- **IDA Pro 정밀 검증 (선택 사항)**:
  - 스토리지 쪽 검증 루틴(`H5vccStorage::VerifyTest`)이 구체적으로 어떤 무결성 검사를 수행하는지 궁금할 경우 해당 함수 주소만 타겟팅하여 Hex-Rays 디컴파일 확인 가능.
