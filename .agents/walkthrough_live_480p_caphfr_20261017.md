# 작업 리포트: 라이브 480p 캡 해제 (capHfr 게이트)

> **작업 일시**: 2026-10-17
> **증상**: 1080p 라이브 방송이 480p(`large`)로만 재생, 화질 메뉴에 HD 없음,
>   네트워크와 무관하게 상향 없음. 동일 기기 YTN 라이브는 1080p 정상.

---

## 1. 근본 원인 (실측으로 확정)

| 단계 | 결과 |
| :--- | :--- |
| 서버 제공 포맷 (InnerTube 실응답 스눕) | 1080p60(299/303), 720p60(298/302) 포함 13개 정상 수신 |
| `MediaSource`/`decodingInfo` 지원 판정 | 1080p60 H264/VP9 exact mime 전부 통과 |
| 패치 적용 여부 (페이지 내 JS 재取得) | B3/k2/default/live/hfr/random 전부 적용 중 |
| localStorage 성능 캡 | 비어 있음 |

남은 게이트는 포맷 블록리스트 `gv()`의 HFR 규칙이었음:

```js
if((B=L.video)==null?0:B.fps>32){
  if(!v.Fx&&!HH(v,j6.FRAMERATE))return"capHfr"; ...
```

`HH(FRAMERATE)`는 정상값(`framerate=30`)과 불가능값(`framerate=9999`)을
동시에 물어 거짓말을 가려냄. 기존 MSE 오버라이드가 **둘 다 참**으로 답해
무결성 검사를 깨뜨렸고, 그 결과 fps>32 포맷 전체가 탈락 → 60fps HD만 있는
라이브는 480p로 고착. 30fps 방송(YTN)은 규칙을 타지 않아 정상이었던 것과 일치.

## 2. 변경 내용

1. **`h5vcc_polyfill.js` — MSE 정직화**:
   `width/height/framerate/bitrate` 파라미터 포함 조회는 실측값으로 통과
   (무결성 검사 정상화). 파라미터 없는 bare codec 조회는 기존 affirm 유지
   (포맷 리스팅 언락 보존).
2. **`TVWebViewClient.kt`**:
   - `gv()` HFR 게이트 무력화 (`if(!v.Fx&&!HH(...))return"capHfr"` → `if(!1)...`,
     단일 발생 확인).
   - `/dev/null`이 아닌 실질 캡 3종 무력화는 전회분 유지
     (`html5_live_quality_cap`, `html5_hfr_quality_cap`,
     `html5_random_playback_cap` → `_k2off` 리네임).
   - `PATCH_VERSION` 2 → 3 (디스크 패치 캐시 무효화).
3. 패치 시뮬레이션(실제 플레이어 JS 2.4MB 대상): 전 패턴 정확히 1회 매칭,
   잔여 없음, 패치 후 전체 파일 `node --check` 통과. `blk8khfr`(8K),
   `disablevp9hfr`(DRM), `ratecap` 등 정당한 규칙은 보존.

## 3. 실기기 검증 (OsqH1F_BL1I 동일 방송)

- 래더: `[large, medium, small, auto]` → **`[hd1080, hd720, large, medium,
  small, auto]`** (메뉴 조정 가능).
- 재생: `hd1080` 자동 선택, 1920x1080.
- 안정성: 20초간 60fps 1226프레임 중 드롭 3개(0.25%) — 1080p60 디코딩 여유.
  인위적 캡이었음이 하드웨어로도 입증됨.
- VOD 회귀 없음: 4K VOD 래더 `hd2160`까지 완전, `hd2160` 재생 중.
