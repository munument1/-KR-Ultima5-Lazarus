# 울티마 V: 라자루스 한국어 패치

Dungeon Siege 1 기반 리메이크 모드 **Ultima V: Lazarus 1.20**의 한국어 번역 프로젝트입니다.

현재 공개본은 **B097 프리뷰**입니다. 번역표 B001~B096의 23,907개 항목과 별도 잔존 문자열 57곳을 게임 리소스에 반영했습니다. 게임 원본 DSRES는 저장소에 포함하지 않으며, 설치 도구가 사용자의 원본 파일에 델타를 적용합니다.

## 준비물

- Windows용 Dungeon Siege 1
- Ultima V: Lazarus 1.20
- Python 3.10 이상
- 한국어를 출력할 수 있는 Dungeon Siege `Language.dsres`

기본 설치 예시는 다음 경로를 사용합니다.

```text
C:\Games\Steam\steamapps\common\Dungeon Siege 1
```

## 한국어 패치 설치

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

## 한글 폰트 적용

본문 패치와 별도로 Lazarus 대화용 폰트 키를 한글 글꼴에 연결해야 합니다. `tools/build_font_test.py`는 사용자가 보유한 한국어판 `Language.dsres`를 기반으로 새 파일을 만듭니다.

```powershell
python tools\build_font_test.py `
  "C:\원본한국어판\Resources\Language.dsres" `
  --language-dll "C:\원본한국어판\Language.dll"
```

기본 매핑은 다음과 같습니다.

```text
b_gui_fnt_20p_laztalk = "굴림,18";
```

생성된 `U5L_Korean_Font_Test`의 `Language.dll`과 `Resources\Language.dsres`를 게임 폴더의 같은 위치에 넣습니다. 기존 파일은 먼저 백업하세요. 다른 글꼴은 `--font`, 크기는 `--size`로 지정할 수 있습니다.

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
- B001~B096 한국어 빈칸 0개
- DSRES 재추출 및 비수정 리소스 무결성 검증
- 대화 텍스트 참조 34,871개와 저장 항목 34,877개 검증
- B097의 활성 영문 잔존 57곳 추가 반영

세부 검증 수치는 [검증 기록](docs/VERIFICATION.md)을 참고하세요.

## 알려진 제한

- 일부 서적은 페이지 넘김을 반복하면 같은 위치로 돌아갑니다. 위아래 스크롤로 전체 본문을 읽을 수 있고 X 버튼은 정상 동작합니다.
- 환경에 따라 글자 `떻`의 모양이 깨질 수 있으나 문맥은 판독 가능합니다.
- 간판·효과음 자막 등 PSD 이미지에 그려진 81개 텍스트는 이번 패치 대상이 아닙니다.
- B097은 정적 무결성 검증을 통과했지만 전체 플레이 회귀 테스트는 계속 진행 중입니다.

## 번역 데이터와 도구

- `translations/B001-B095.tsv`: 기본 번역 및 검수 데이터
- `translations/B096.tsv`: 추출 QA에서 보강한 172개 항목
- `translations/B097_residual_patches.json`: 위치 한정 잔존 문자열 검증 기록
- `tools/apply_korean_patch.py`: 사용자 원본에 한국어 패치 설치
- `tools/build_font_test.py`: 사용자 소유 한국어 `Language.dsres`에 Lazarus 폰트 키 추가
- `tools/make_u5k_delta.py`: 유지보수용 델타 생성기

## 저작권과 라이선스

이 저장소는 Dungeon Siege, Ultima V: Lazarus, 한국 정발판의 원본 로직 DSRES, `Language.dll`, `Language.dsres`를 배포하지 않습니다. 델타는 사용자가 합법적으로 보유한 Lazarus 1.20 원본에만 적용됩니다. `zzz_U5K_Text_OnDemand.dsres`는 이 프로젝트에서 생성한 한국어 문자열 저장용 탱크입니다.

저장소에서 직접 작성한 도구 코드는 [MIT License](LICENSE)로 배포합니다. 게임 원본 데이터와 제3자 자산에는 이 라이선스가 적용되지 않습니다.
