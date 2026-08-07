# 울티마 V: 라자루스 한국어화

**Ultima V: Lazarus 한국어 번역 프로젝트**입니다.

> 현재 번역은 진행 중입니다. 이 저장소는 완성 배포본이 아니라 작업 소스와 한국어 출력 테스트 도구를 먼저 공개하기 위한 저장소입니다.

## 현재 상태

- [x] Dungeon Siege 1 한국어 로캘 및 기본 UI 한글 출력 확인
- [x] 한국 정발판의 `gui_font_map` 방식 확인
- [x] Lazarus 대화용 논리 폰트 `b_gui_fnt_20p_laztalk`를 Windows 한글 폰트로 연결하는 테스트 도구 작성
- [x] Ultima V: Lazarus 정상 실행 및 게임 내부 공용 UI 한글 출력 확인
- [ ] Lazarus 실제 NPC 대화에서 한글 출력 최종 확인
- [ ] Lazarus 본문 번역 완료
- [ ] 전체 UI/대사 검수 및 배포 패키지 제작

---

# 설치 전에 꼭 읽어주세요

Ultima V: Lazarus는 독립 실행형 게임이 아니라 **Dungeon Siege 1 엔진에서 별도 리소스를 불러 실행하는 모드/리메이크**입니다.

따라서 파일을 제대로 넣어도 **바로가기의 실행 파일 경로와 `map_paths`, `res_paths`가 틀리면 기본 Dungeon Siege 1 캠페인이 실행됩니다.**

이 경우 대표적으로 **Stonebridge(스톤브릿지)**가 나오며, 한글패치가 잘못된 것처럼 보일 수 있습니다.

## 1. Lazarus 리소스 위치 확인

먼저 Dungeon Siege 1의 `Resources` 폴더 안에 Lazarus 리소스가 실제로 존재하는지 확인하세요.

예:

```text
C:\Games\Steam\steamapps\common\Dungeon Siege 1\Resources\lazarus_art.dsres
C:\Games\Steam\steamapps\common\Dungeon Siege 1\Resources\lazarus_logic.dsres
```

설치 환경에 따라 파일 이름은 더 있을 수 있습니다.

핵심은 **`lazarus_*.dsres` 파일이 들어있는 폴더를 `map_paths`와 `res_paths`가 가리켜야 한다는 것**입니다.

## 2. Lazarus 바로가기 설정

Steam판 기준으로 실제 `DungeonSiege.exe`가 다음 위치에 설치되어 있다고 가정합니다.

```text
C:\Games\Steam\steamapps\common\Dungeon Siege 1\DungeonSiege.exe
```

그리고 Lazarus 리소스가 다음 폴더에 있다면:

```text
C:\Games\Steam\steamapps\common\Dungeon Siege 1\Resources
```

바로가기의 **대상(Target)** 을 다음처럼 설정합니다.

```text
"C:\Games\Steam\steamapps\common\Dungeon Siege 1\DungeonSiege.exe" map_paths=!"C:\Games\Steam\steamapps\common\Dungeon Siege 1\Resources" res_paths="C:\Games\Steam\steamapps\common\Dungeon Siege 1\Resources"
```

바로가기의 **시작 위치(Start in)** 는 다음처럼 설정하는 것을 권장합니다.

```text
C:\Games\Steam\steamapps\common\Dungeon Siege 1
```

### 매우 중요

다음처럼 실행 파일이 엉뚱한 위치를 가리키면 문제가 생길 수 있습니다.

```text
C:\DungeonSiege.exe
```

Steam판을 사용한다면 가능한 한 **Steam 설치 폴더 안의 실제 `DungeonSiege.exe`를 직접 지정**하세요.

또한 `map_paths`의 `!`를 빼먹지 마세요.

---

# 자주 발생하는 문제

## 게임을 실행했는데 Stonebridge가 나옵니다

이것은 대개 **한글패치 문제가 아닙니다.**

기본 Dungeon Siege 1 캠페인이 실행된 상태입니다.

다음을 확인하세요.

1. 바로가기의 실행 파일이 실제 Dungeon Siege 설치 폴더의 `DungeonSiege.exe`인지
2. `map_paths=!"..."`가 Lazarus 리소스 폴더를 가리키는지
3. `res_paths="..."`도 같은 Lazarus 리소스 폴더를 가리키는지
4. 해당 폴더 안에 실제로 `lazarus_art.dsres`, `lazarus_logic.dsres` 등의 파일이 있는지

Lazarus 캐릭터 선택/생성 화면까지 들어왔다면 Lazarus 리소스 로딩은 된 것입니다.

## 캐릭터 생성 화면에서 진행 버튼이 안 보이거나 클릭할 수 없습니다

먼저 **화면 해상도 때문에 UI 하단이 잘린 것은 아닌지 확인하세요.**

Dungeon Siege 1/Lazarus의 오래된 UI는 일부 고해상도나 화면 비율에서 화면 아래쪽 버튼이 잘릴 수 있습니다.

증상 예:

- 캐릭터 생성 화면은 정상적으로 보임
- 키를 눌러도 진행되지 않는 것처럼 보임
- 마우스로 누를 진행 버튼이 보이지 않음
- 화면 하단 일부가 잘려 있음

이 경우 게임 해상도를 낮춘 뒤 다시 확인하세요. **패치나 입력 장치 문제로 단정하기 전에 반드시 화면 아래쪽 UI가 전부 보이는지 확인하는 것이 좋습니다.**

## 옵션과 게임 내부 UI가 한국어로 나옵니다

정상입니다.

Dungeon Siege 한국어판의 `Language.dsres`에는 Dungeon Siege 엔진이 공통으로 사용하는 UI 문자열이 포함되어 있어, Lazarus 내부에서도 공용 UI가 한국어로 표시될 수 있습니다.

다만 이것이 **Lazarus 고유 NPC 대사와 퀘스트 본문까지 번역되었다는 뜻은 아닙니다.** Lazarus 전용 텍스트 번역은 별도 작업입니다.

---

# 한글 폰트 테스트 도구

`tools/build_font_test.py`는 사용자가 보유한 **Dungeon Siege 한국어판 `Language.dsres`**를 읽어,
Lazarus의 대화용 폰트 키를 Windows 글꼴에 연결한 테스트 파일을 만듭니다.

기본 매핑:

```text
b_gui_fnt_20p_laztalk = "굴림,18";
```

## 사용법

Python 3만 있으면 됩니다. 외부 패키지는 필요하지 않습니다.

```bash
python tools/build_font_test.py "C:\Dungeon Siege\Resources\Language.dsres" \
  --language-dll "C:\Dungeon Siege\Language.dll"
```

생성 결과:

```text
U5L_Korean_Font_Test/
├─ Language.dll
└─ Resources/
   └─ Language.dsres
```

게임에 넣기 전에 기존 `Language.dll`과 `Resources/Language.dsres`는 반드시 백업하세요.

다른 Windows 한글 폰트를 시험하려면:

```bash
python tools/build_font_test.py "...\Language.dsres" --font "맑은 고딕" --size 18
```

---

# 확인된 원리

Dungeon Siege 한국어판은 모든 한글을 별도 비트맵 폰트로 만드는 방식이 아니라,
`config/global_settings.gas`의 `[gui_font_map]`에서 게임 내부 폰트 키를 Windows 설치 글꼴에 연결합니다.

이 프로젝트는 그 구조를 이용해 Lazarus의 `b_gui_fnt_20p_laztalk`에도 한글 글꼴을 연결하는 방법을 시험하고 있습니다.

현재까지 확인된 것은 다음과 같습니다.

- Dungeon Siege 한국어 로캘 정상 동작
- 기본 및 공용 UI 한글 표시 정상
- Ultima V: Lazarus 정상 실행
- Lazarus 게임 내부 진입 정상
- Lazarus 내부 공용 UI 한글 표시 정상

Lazarus 고유 NPC 대사 및 퀘스트 문자열은 번역 작업 진행 후 별도 검증할 예정입니다.

---

# 저작권 / 배포 방침

이 저장소에는 Dungeon Siege, Ultima V: Lazarus 또는 기존 한국 정발판의 원본 게임 데이터,
`Language.dll`, `Language.dsres` 등 **저작권이 있는 바이너리 리소스를 포함하지 않습니다.**
테스트 스크립트는 사용자가 합법적으로 보유한 파일을 로컬에서 변환하도록 설계되어 있습니다.

번역 데이터 역시 작업 및 권리 관계를 정리한 뒤 별도로 추가할 예정입니다.

## 라이선스

이 저장소에서 직접 작성한 도구 코드는 MIT License로 배포합니다. 게임 원본 데이터와 제3자 자산에는 적용되지 않습니다.
