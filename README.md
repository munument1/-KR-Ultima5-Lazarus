# 울티마 V: 라자루스 한국어 패치

Dungeon Siege 1 기반 리메이크 모드 **Ultima V: Lazarus 1.20**의 한국어 번역 프로젝트입니다.

현재 공개본은 **B102 프리뷰**입니다. 번역표 B001~B096의 23,907개 항목과 B097 잔존 문자열 57곳에 더해, Lazarus 1.20 원본 전체 재검수에서 확인한 표시 문구 479곳을 추가 반영했습니다. 바로 붙여넣는 완성 패키지와 원본 보존형 델타 설치 방식을 함께 제공합니다.

## 준비물

- Windows용 Dungeon Siege 1
- Ultima V: Lazarus 1.20

기본 설치 예시는 다음 경로를 사용합니다.

```text
C:\Games\Steam\steamapps\common\Dungeon Siege 1
```

## 가장 간단한 설치: Resources 붙여넣기

1. 게임 폴더의 `Resources\lazarus_logic.dsres`, `Resources\britannia_logic.dsres`, 기존 `Resources\Language.dsres`와 `Language.dll`이 있다면 모두 백업합니다.
2. [`Ultima_V_Lazarus_Korean_B102_Copy_Paste.zip`](release/Ultima_V_Lazarus_Korean_B102_Copy_Paste.zip)을 받아 압축을 풉니다.
3. 압축 안의 `Copy_to_Dungeon_Siege_1` 폴더 내용 전체를 Dungeon Siege 1 폴더에 그대로 붙여넣고 덮어씁니다.
4. `Create_Ultima_V_Lazarus_Shortcut.cmd`를 더블클릭합니다.
5. 바탕화면에 만들어진 `Ultima V - Lazarus v1.20` 바로가기로 실행합니다.

ZIP SHA-256: `554AFDE77CD5BD8A4159200703FCF78D8510948113F82AD6FBBB94D4D44C8BD3`

기본 붙여넣기 대상은 다음 위치입니다.

```text
C:\Games\Steam\steamapps\common\Dungeon Siege 1
```

붙여넣기 폴더에는 Steam 호환형 `Language.dll`, 원래 글꼴 매핑을 보존한 `Language.dsres`, Lazarus 대화 글꼴 매핑이 함께 들어 있습니다. **별도의 Dungeon Siege 1 한글 패치를 먼저 설치할 필요가 없습니다.** 본편 한국어 음성용 `Voices.dsres`는 Lazarus 한글 출력에 필요하지 않아 제외했습니다.

Steam 호환형 `Language.dll`은 기존 한국어 리소스 429개의 내용을 바이트 단위로 모두 보존하고 PE 리소스 컨테이너만 Windows API로 다시 패킹했습니다. 기존 DLL에서 게임 종료 시 발생하던 SmartHeap `MEM_BAD_POINTER` 경고가 재패킹본에서는 나타나지 않는 것을 실기로 확인했습니다.

## 원본 파일 보존형 설치: Python 델타

게임 원본을 포함한 완성 DSRES를 직접 받지 않고 사용자 원본에서 생성하려면 다음 방식을 사용합니다. Python 3.10 이상이 필요합니다.

먼저 게임의 `Resources` 폴더에 수정되지 않은 Lazarus 1.20 원본 파일이 있어야 합니다.

```text
Resources\lazarus_logic.dsres
Resources\britannia_logic.dsres
```

저장소 루트에서 다음 명령을 실행합니다.

```powershell
python tools\apply_korean_patch.py "C:\Games\Steam\steamapps\common\Dungeon Siege 1"
```

설치 도구는 다음 순서로 동작합니다.

1. 두 원본 파일의 SHA-256과 버전을 확인합니다.
2. 패치 결과를 임시 폴더에 생성하고 다시 SHA-256으로 검증합니다.
3. 게임 폴더의 `KoreanPatchBackups`에 원본을 백업합니다.
4. 검증된 로직 파일과 한국어 텍스트 탱크를 `Resources`에 설치합니다.

지원하지 않는 해시가 나오면 다른 모드나 과거 패치로 변형된 파일입니다. Lazarus 1.20 원본 두 파일을 복원한 뒤 다시 실행하세요.

## 다른 한글 패치나 글꼴 사용

붙여넣기 패키지는 `굴림 18` 글꼴이 설정된 한국어 `Language.dsres`를 포함하므로 이 과정은 선택 사항입니다. 다른 Dungeon Siege 1 한글 패치나 Windows 글꼴을 사용하려면 `tools/build_font_test.py`로 사용자의 `Language.dsres`를 보강할 수 있습니다.

제공받은 Dungeon Siege 1 한글 패치는 글꼴 하나만 쓰지 않습니다. 활성 매핑은 기본·12p·자막에 `굴림`, 14p·16p·20p에 `궁서`를 사용합니다. B102는 이 여섯 매핑을 그대로 보존하고 Lazarus 대화용 `굴림 18` 매핑 하나만 추가합니다.

```powershell
python tools\build_font_test.py `
  "C:\원본한국어판\Resources\Language.dsres"
```

기본 매핑은 다음과 같습니다.

```text
b_gui_fnt_20p_laztalk = "굴림,18";
```

생성된 `U5L_Korean_Font_Test\Resources\Language.dsres`를 게임 폴더의 같은 위치에 넣습니다. 기존 파일은 먼저 백업하세요. 다른 글꼴은 `--font`, 크기는 `--size`로 지정할 수 있습니다. `Language.dll`은 붙여넣기 패키지에 포함된 Steam 호환본을 유지하세요.

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

게임을 실행했을 때 Stonebridge가 나오면 기본 캠페인이 열린 것입니다. 실행 파일 경로, `map_paths`의 `!`, `res_paths`, Lazarus 리소스 위치를 다시 확인하세요.

## 확인된 상태

- 인트로와 시스템 초기화 문구 출력
- 아이올로 일반 대화 진행
- 사망 처리 후 월드 이동
- 서적 본문 114권 한국어 출력 및 닫기 버튼 동작
- 서적 페이지 이동·세로 스크롤 동작이 원본 Lazarus와 동일함을 확인
- B001~B096 한국어 빈칸 0개
- DSRES 재추출 및 비수정 리소스 무결성 검증
- 대화 텍스트 참조 34,871개와 저장 항목 34,877개 검증
- B097의 활성 영문 잔존 57곳 추가 반영
- Lazarus 1.20 원본 전체 재검수 표시 문구 479곳 추가 반영
- 확정 표시 미번역 및 동적 호칭 잔존 0건

세부 검증 수치는 [검증 기록](docs/VERIFICATION.md)을 참고하세요.

## 알려진 제한

- 환경에 따라 글자 `떻`의 모양이 깨질 수 있으나 문맥은 판독 가능합니다.
- 간판·효과음 자막 등 PSD 이미지에 그려진 81개 텍스트는 이번 패치 대상이 아닙니다.
- B102는 정적 무결성 검증을 통과했지만 추가 문구의 게임 내 회귀 테스트는 계속 진행 중입니다.

## 번역 데이터와 도구

- `translations/B001-B095.tsv`: 기본 번역 및 검수 데이터
- `translations/B096.tsv`: 추출 QA에서 보강한 172개 항목
- `translations/B097_residual_patches.json`: 위치 한정 잔존 문자열 검증 기록
- `translations/B099_Static_Translation.tsv`: 재검수에서 보강한 UI·주문·아이템 문구
- `translations/B098-B102_reaudit_summary.json`: 전체 재검수 단계와 제외 사유 요약
- `tools/apply_korean_patch.py`: 사용자 원본에 한국어 패치 설치
- `tools/build_font_test.py`: 사용자 소유 한국어 `Language.dsres`에 Lazarus 폰트 키 추가
- `tools/make_u5k_delta.py`: 유지보수용 델타 생성기
- `release/Copy_to_Dungeon_Siege_1`: 붙여넣기용 완성 파일과 바로가기 생성 도구

## 저작권과 라이선스

붙여넣기용 `lazarus_logic.dsres`, `britannia_logic.dsres`, `Language.dsres`, `Language.dll`은 한국어 출력을 위해 포함하거나 수정한 리소스이며 게임·모드·기존 한국어 데이터의 권리는 각 권리자에게 있습니다. 이 파일들은 MIT License 적용 대상이 아닙니다. 수정 로직 DSRES 배포를 피하려는 경우 Python 델타 설치 방식을 사용할 수 있습니다.

저장소에서 직접 작성한 도구 코드는 [MIT License](LICENSE)로 배포합니다. 게임 원본 데이터와 제3자 자산에는 이 라이선스가 적용되지 않습니다.
