## Ultima V: Lazarus 한국어 패치 B104 Runtime QA

B103 이후 실제 게임 코드의 화면 출력 경로를 다시 감사하여 기존 번역 추출 범위 밖에 남아 있던 대화 선택지와 동적 인명/호칭, 일부 시스템 문구를 보완한 프리뷰입니다.

### B104 변경 사항

- 고정 영문 대화 선택지 `add_keyword$` 1,246곳 한국어화
- 대응 `remove_keyword$` 1,188곳을 같은 표시값으로 동기화
- 183개 대화 스크립트의 동적 인명/호칭 517곳 보완
- `Provisions`, `Poison` 등 선택지 잔존 영문 보완
- 트레이너 `Destruction / Protection` 표시·선택 판정 동시 보완
- 주문 무효화 시 `fizzle...` 시스템 메시지 번역
- Shadowlord 화면명 Faulinei / Astaroth / Nosfentor 보완
- Words of Power·암호·만트라는 게임 의미 보존을 위해 원문 유지

### 정적 검증

- `lazarus_logic` 1,113 / `britannia_logic` 651 / OnDemand 308 리소스 전수 재추출 성공
- 외부 한국어 팩 886개, 참조 38,585개: 누락 0 / 잘못된 인덱스 0
- 수정 SKRIT 267개 구조 오류 0
- 재생성 DSRES와 작업 입력 바이트 불일치 0

### 설치

첨부 ZIP을 풀고 `Copy_to_Dungeon_Siege_1` 폴더의 내용 전체를 Dungeon Siege 1 게임 폴더에 붙여넣습니다. 기존 로직/Language 파일은 먼저 백업하세요.

### 주의

B104는 Runtime QA 프리뷰입니다. 정적 검증은 통과했지만 신규 보완분의 최종 기준은 실제 Dungeon Siege 1 게임 내 테스트입니다. PSD 이미지형 효과음·간판 텍스트 81개는 기존과 동일하게 제외되어 있습니다.

### SHA-256

`Ultima_V_Lazarus_Korean_B104_Copy_Paste.zip`

`AA3EC07533E6FFADDE1750CDA6A192F7A213315018E1E99020EA6CA3A89270BC`
