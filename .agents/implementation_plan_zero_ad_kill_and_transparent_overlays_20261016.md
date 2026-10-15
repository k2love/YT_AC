# YouTube TV 클린룸: 1~2초 후 강제광고 원천 차단 및 오버레이/제목 투명화 계획서

## 1. 개요 및 사용자 피드백 분석
- **보고된 문제**:
  1. 영상 재생 후 1~2초 뒤에 강제광고가 뜸.
  2. 유튜브 로고 뒷배경이 여전히 투명하지 않고, 컨트롤 메뉴 및 영상 제목들도 불투명한 배경이 깔려 있음.
- **근본 원인 규명**:
  1. 유튜브 플레이어(`tv-player-ias.js`)가 비디오 시작 직후 `adBreakHeartbeatParams`를 통해 비동기 Ad Break(1~2초 시점 프리롤/미드롤 광고)를 서버에서 동적으로 수신함.
  2. 안드로이드 WebView의 GPU 컴포지터가 CSS `linear-gradient`의 반투명 알파 블렌딩을 시커먼 불투명 사각 박스로 렌더링하는 버그 발생 -> 컨트롤 바(`.ytp-chrome-bottom`, `.ytp-gradient-bottom`) 및 영상 제목(`.ytp-chrome-top`, `.ytp-gradient-top`, `.ytp-title`) 전체에 검은 박스가 덮임.
  3. `#loader` 주변 `body`와 컨테이너에 다크 그레이 `#1c1a1a`가 남아있어 로고 뒤에 이질적인 배경이 뜸.

## 2. 해결 구현 계획
1. **1~2초 후 광고 원천 차단 (Zero-Ad 3중 킬스위치)**:
   - `adBreakHeartbeatParams` 게터를 `undefined`로 설정하여 비동기 광고 하트비트 스케줄러 자체를 비활성화.
   - `TVWebViewClient.kt`에서 `ad_break`, `get_midroll_info`, `pagead`, `ptracking` 요청을 네이티브 204로 완전 차단.
   - 25ms 초고속 `instantAdKiller`를 탑재하여 광고 큐 발생 즉시 `player.skipAd()` + 16배속 강제 종결.
2. **컨트롤 메뉴, 영상 제목 및 오버레이 100% 완전 투명화**:
   - `.ytp-gradient-bottom`, `.ytp-gradient-top`, `.ytp-chrome-bottom`, `.ytp-chrome-top`, `.ytp-title` 등의 `background-image`를 `none !important;`, `background`를 `transparent !important;`로 설정하여 불투명 박스를 원천 제거.
   - 텍스트에는 부드러운 그림자(`text-shadow: 0 1px 4px rgba(0,0,0,0.8)`)를 적용하여 투명 영상 위에서 제목과 컨트롤 아이콘만 또렷하게 부유하도록 복원.
3. **유튜브 로고 및 런처 리얼 블랙 일체화**:
   - `html, body, #container, #app-background`를 순정 OLED 리얼 블랙(`#000000`)으로 일체화하고 `#loader` 배경을 완전 투명(`transparent`) 처리.
4. **빌드 및 실기기 검증**:
   - `gradlew.bat assembleDebug` 성공 확인.
