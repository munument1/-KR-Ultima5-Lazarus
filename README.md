# 울티마 V: 라자루스 한국어화

**Ultima V: Lazarus 한국어 번역 프로젝트**입니다.

> 현재 번역은 진행 중입니다. 이 저장소는 완성 배포본이 아니라 작업 소스와 한국어 출력 테스트 도구를 먼저 공개하기 위한 저장소입니다.

## 현재 상태

- [x] Dungeon Siege 1 한국어 로캘 및 기본 UI 한글 출력 확인
- [x] 한국 정발판의 `gui_font_map` 방식 확인
- [x] Lazarus 대화용 논리 폰트 `b_gui_fnt_20p_laztalk`를 Windows 한글 폰트로 연결하는 테스트 도구 작성
- [ ] Lazarus 실제 NPC 대화에서 한글 출력 최종 확인
- [ ] Lazarus 본문 번역 완료
- [ ] 전체 UI/대사 검수 및 배포 패키지 제작

## 한글 폰트 테스트 도구

`tools/build_font_test.py`는 사용자가 보유한 **Dungeon Siege 한국어판 `Language.dsres`**를 읽어,
Lazarus의 대화용 폰트 키를 Windows 글꼴에 연결한 테스트 파일을 만듭니다.

기본 매핑:

```text
b_gui_fnt_20p_laztalk = "굴림,18";
```

### 사용법

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

## 확인된 원리

Dungeon Siege 한국어판은 모든 한글을 별도 비트맵 폰트로 만드는 방식이 아니라,
`config/global_settings.gas`의 `[gui_font_map]`에서 게임 내부 폰트 키를 Windows 설치 글꼴에 연결합니다.

이 프로젝트는 그 구조를 이용해 Lazarus의 `b_gui_fnt_20p_laztalk`에도 한글 글꼴을 연결하는 방법을 시험하고 있습니다.

## 저작권 / 배포 방침

이 저장소에는 Dungeon Siege, Ultima V: Lazarus 또는 기존 한국 정발판의 원본 게임 데이터,
`Language.dll`, `Language.dsres` 등 **저작권이 있는 바이너리 리소스를 포함하지 않습니다.**
테스트 스크립트는 사용자가 합법적으로 보유한 파일을 로컬에서 변환하도록 설계되어 있습니다.

번역 데이터 역시 작업 및 권리 관계를 정리한 뒤 별도로 추가할 예정입니다.

## 라이선스

이 저장소에서 직접 작성한 도구 코드는 MIT License로 배포합니다. 게임 원본 데이터와 제3자 자산에는 적용되지 않습니다.
