# 울티마 V: 라자루스 한국어 패치

Dungeon Siege 1 기반 리메이크 모드 **Ultima V: Lazarus 1.20**의 한국어 번역 프로젝트입니다.

현재 공개본은 **B104 Runtime QA 프리뷰**입니다. B103까지의 본문·UI·서적·NPC 명칭 보완에 더해, 실제 실행 코드의 화면 출력 경로를 다시 감사하여 대화 선택지, 동적 인명/호칭, 일부 시스템 메시지에서 남아 있던 영문을 추가로 보완했습니다.

## 준비물

- Windows용 Dungeon Siege 1
- Ultima V: Lazarus 1.20

기본 설치 예시는 다음 경로를 사용합니다.

```text
C:\Games\Steam\steamapps\common\Dungeon Siege 1
```

## 가장 간단한 설치: Resources 붙여넣기

1. 게임 폴더의 `Resources\lazarus_logic.dsres`, `Resources\britannia_logic.dsres`, 기존 `Resources\Language.dsres`와 `Language.dll`이 있다면 모두 백업합니다.
2. [`Ultima_V_Lazarus_Korean_B104_Copy_Paste.zip`](release/Ultima_V_Lazarus_Korean_B104_Copy_Paste.zip)을 받아 압축을 풉니다.
3. 압축 안의 `Copy_to_Dungeon_Siege_1` 폴더 내용 전체를 Dungeon Siege 1 폴더에 그대로 붙여넣고 덮어씁니다.
4. `Create_Ultima_V_Lazarus_Shortcut.cmd`를 더블클릭합니다.
5. 바탕화면에 만들어진 `Ultima V - Lazarus v1.20` 바로가기로 실행합니다.

ZIP SHA-256: `F06ADB7238782F6580D1C2A73D07D2F7EE08564BEE470B405D3DE2DB5A643FF6`

붙여넣기 폴더에는 Steam 호환형 `Language.dll`, 한국어 `Language.dsres`, Lazarus 대화 글꼴 매핑이 함께 들어 있습니다. **별도의 Dungeon Siege 1 한글 패치를 먼저 설치할 필요가 없습니다.**

## B104에서 추가된 내용

- 일반 게임 대화의 고정 영문 선택지 `add_keyword$` **1,246곳** 한국어화
- 대응 `remove_keyword$` **1,188곳**을 동일 표시값으로 동기화
- **183개 대화 스크립트 / 517곳**의 동적 NPC 이름·호칭 영문 누출 보완
- `Provisions`, `Poison` 등 기존 번역은 있었지만 선택지에 남아 있던 항목 보완
- 트레이너 `Destruction / Protection` → `파괴 / 보호` 및 선택 판정 동기화
- 주문 무효화 시 `fizzle...` → `주문이 무효화되었다...`
- Shadowlord 화면명 `Faulinei / Astaroth / Nosfentor` 한국어 표기 보완
- Words of Power, 암호, 만트라처럼 게임 안에서 원문 자체가 의미를 갖는 문자열은 의도적으로 유지

## 원본 파일 보존형 Python 델타 설치

저장소의 기존 Python 델타 설치기는 **B103 계열용으로 보존**되어 있습니다. **B104 Runtime QA 테스트판은 위의 붙여넣기 ZIP 설치를 사용하세요.** B104가 게임 내 확인까지 끝난 뒤 원본 보존형 델타도 같은 결과로 갱신할 예정입니다.

## 다른 한글 패치나 글꼴 사용

붙여넣기 패키지는 `굴림 18` 글꼴이 설정된 한국어 `Language.dsres`를 포함합니다. 다른 Dungeon Siege 1 한글 패치나 Windows 글꼴을 사용하려면 `tools/build_font_test.py`를 이용할 수 있습니다.

기존 한국어 리소스의 활성 글꼴 매핑을 보존하고 Lazarus 대화용 매핑을 추가합니다.

```text
b_gui_fnt_20p_laztalk = "굴림,18";
```

## Lazarus 실행 바로가기

파일을 제대로 설치해도 실행 옵션이 틀리면 Lazarus가 아니라 기본 Dungeon Siege 캠페인이 시작됩니다. Steam 기본 경로를 쓴다면 바로가기 속성을 다음처럼 설정합니다.

대상:

```text
"C:\Games\Steam\steamapps\common\Dungeon Siege 1\DungeonSiege.exe" map_paths=!"C:\Games\Steam\steamapps\common\Dungeon Siege 1\Resources" res_paths="C:\Games\Steam\steamapps\common\Dungeon Siege 1\Resources"
```

시작 위치:

```text
C:\Games\Steam\steamapps\common\Dungeon Siege 1
```

## B104 정적 검증

- `lazarus_logic.dsres`: 1,113개 리소스 전체 재추출 성공
- `britannia_logic.dsres`: 651개 리소스 전체 재추출 성공
- `zzz_U5K_Text_OnDemand.dsres`: 308개 리소스 전체 재추출 성공
- 외부 한국어 텍스트 팩 **886개** 검사
- 외부 텍스트 참조 **38,585개**: 팩 누락 0, 인덱스 오류 0
- 최대 텍스트 팩 크기 12,000 bytes (`< 16,384`)
- 수정 SKRIT **267개**: 문자열/중괄호/소괄호 구조 오류 0
- 생성된 세 DSRES를 다시 풀어 입력 트리와 바이트 비교: 불일치 0

세부 검증 수치는 [검증 기록](docs/VERIFICATION.md)을 참고하세요.

## 알려진 제한

- 간판·효과음 자막 등 PSD 이미지에 그려진 **81개 텍스트**는 이번 패치 대상이 아닙니다.
- 환경에 따라 글자 `떻`의 모양이 깨질 수 있으나 문맥은 판독 가능합니다.
- B104는 정적 무결성 검증을 통과한 **Runtime QA 프리뷰**입니다. 실제 Dungeon Siege 1 엔진에서의 게임 내 확인이 최종 기준입니다.

## 번역 데이터와 도구

- `translations/B001-B095.tsv`: 기본 번역 및 검수 데이터
- `translations/B096.tsv`: 추출 QA에서 보강한 항목
- `translations/B097_residual_patches.json`: 위치 한정 잔존 문자열 검증 기록
- `translations/B099_Static_Translation.tsv`: 재검수에서 보강한 UI·주문·아이템 문구
- `translations/B098-B103_reaudit_summary.json`: B103까지의 전체 재검수 요약
- `translations/B104_runtime_qa_summary.json`: B104 런타임 잔존 영문 감사 및 보완 요약
- `tools/ds1_tank_tool.py`: Dungeon Siege Tank 추출·재패킹 도구
- `tools/generate_b104_runtime.py`: B103 공개본에서 B104 런타임 보완을 재현하는 생성 도구
- `tools/apply_korean_patch.py`: B103 원본 보존형 델타 설치기
- `tools/build_font_test.py`: 사용자 소유 한국어 `Language.dsres`에 Lazarus 폰트 키 추가

## 저작권과 라이선스

붙여넣기용 `lazarus_logic.dsres`, `britannia_logic.dsres`, `Language.dsres`, `Language.dll`은 한국어 출력을 위해 포함하거나 수정한 리소스이며 게임·모드·기존 한국어 데이터의 권리는 각 권리자에게 있습니다. 이 파일들은 MIT License 적용 대상이 아닙니다.

저장소에서 직접 작성한 도구 코드는 [MIT License](LICENSE)로 배포합니다. 게임 원본 데이터와 제3자 자산에는 이 라이선스가 적용되지 않습니다.
