# B104 Runtime QA 검증 기록

## 빌드 결과

| 파일 | 크기 | SHA-256 |
|---|---:|---|
| `lazarus_logic.dsres` | 3,643,696 | `B6A89DB72B1F0966D6162AC3D81A87FACCA4F10E947C924D8E4055287ACB4052` |
| `britannia_logic.dsres` | 1,566,048 | `19920F68F7DBCB7D8A5AD65F397142852BCD05E33F5E4B3A0230723EE70235AD` |
| `zzz_U5K_Text_OnDemand.dsres` | 1,279,416 | `3F40889D369CC265F9E7610B7B08166AD543F98A0C5B5133C249EF44ADDAE4CF` |

붙여넣기 ZIP SHA-256은 `AA3EC07533E6FFADDE1750CDA6A192F7A213315018E1E99020EA6CA3A89270BC`입니다.

변경하지 않은 한국어 런타임 파일:

- `Language.dsres`: `97DD77E56F51A19ED17722A28CCF31C84E99791B717AEEA2646FDF835A52EAA1`
- `Language.dll`: `E59712897B932E80C88DA15165AF5A12475313F4E01C27D41151B3BBA1547559`

## B104 런타임 잔존 영문 감사

- 고정 영문 대화 선택지 `add_keyword$`: 1,246곳 보완
- 대응 `remove_keyword$`: 1,188곳 동기화
- 동적 NPC 이름·호칭: 183개 대화 스크립트, 517곳 보완
- 트레이너 `Destruction / Protection`: 표시와 선택 판정 동시 보완
- Negate Magic 주문 실패 `fizzle...`: 한국어화
- Shadowlord 화면명 `Faulinei / Astaroth / Nosfentor`: 한국어화

의도적으로 유지한 원문:

- Words of Power: `Avidus`, `Fallax`, `Ignavus`, `Infama`, `Inopia`, `Malum`, `Vilis`, `Veramocor`
- 암호/특수어: `Impera`, `Maltari`
- 만트라/음절: `Cah`, `Ra`
- 특수 문맥: `Ni?`
- 개발자용 `conversation_debugger_npc.skrit`

## 정적 검증

- Lazarus 로직 재추출: 1,113개 리소스
- Britannia 로직 재추출: 651개 리소스
- 별도 대화 텍스트 재추출: 308개 리소스
- 외부 한국어 텍스트 팩: 886개
- 외부 한국어 텍스트 조회 참조: 38,585개
- 누락된 텍스트 팩 참조: 0
- 잘못된 텍스트 팩 인덱스: 0
- 최대 텍스트 팩: 12,000 bytes (`< 16,384`)
- 수정 SKRIT: 267개, 문자열/중괄호/소괄호 구조 오류 0
- 세 DSRES 전체 재추출 후 작업 입력과 바이트 불일치 0

## 실기 확인 상태

B098~B103에서 확인한 인트로, 일반 대화, 사망 후 월드 이동, 서적 본문·페이지 이동·세로 스크롤 등 기존 스모크 테스트 결과는 유지됩니다.

**B104 신규 런타임 보완분은 정적 검증까지 완료된 프리뷰이며, 실제 Dungeon Siege 1 엔진에서의 게임 내 테스트가 최종 기준입니다.**

## 의도적으로 제외한 항목

- 주석 처리된 문자열
- 내부 제어 키와 개발자 디버그 대화
- Words of Power·암호·만트라 등 원문 자체가 게임 플레이 의미를 갖는 문자열
- PSD 이미지형 효과음/간판 텍스트 81개
