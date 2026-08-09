#!/usr/bin/env python3
"""Install the Ultima V: Lazarus Korean patch from verified original files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from u5k_delta import DeltaError, apply_delta


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATCH_DIR = PROJECT_ROOT / "patch"
MANIFEST_PATH = PATCH_DIR / "manifest.json"
DEFAULT_GAME_DIR = Path(r"C:\Games\Steam\steamapps\common\Dungeon Siege 1")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def find_resources(argument: Path | None) -> Path:
    candidate = argument or DEFAULT_GAME_DIR
    if candidate.name.casefold() == "resources":
        return candidate
    return candidate / "Resources"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ultima V: Lazarus 1.20 한국어 패치를 설치합니다."
    )
    parser.add_argument(
        "game_dir",
        nargs="?",
        type=Path,
        help="Dungeon Siege 1 폴더 또는 Resources 폴더",
    )
    args = parser.parse_args()

    resources = find_resources(args.game_dir).resolve()
    if not resources.is_dir():
        parser.error(f"Resources 폴더를 찾을 수 없습니다: {resources}")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = manifest["files"]
    originals = ("lazarus_logic.dsres", "britannia_logic.dsres")

    states: dict[str, str] = {}
    for name in originals:
        path = resources / name
        if not path.is_file():
            raise SystemExit(f"필수 파일이 없습니다: {path}")
        actual = sha256_file(path)
        if actual == files[name]["source_sha256"]:
            states[name] = "original"
        elif actual == files[name]["target_sha256"]:
            states[name] = "patched"
        else:
            raise SystemExit(
                f"지원하지 않는 {name}입니다.\n"
                f"현재 SHA-256: {actual}\n"
                "Ultima V: Lazarus 1.20의 수정되지 않은 원본을 복원한 뒤 다시 실행하세요."
            )

    text_tank = PATCH_DIR / "zzz_U5K_Text_OnDemand.dsres"
    if sha256_file(text_tank) != files[text_tank.name]["target_sha256"]:
        raise SystemExit("배포 패키지의 한국어 텍스트 탱크가 손상되었습니다.")

    if all(state == "patched" for state in states.values()):
        installed_text = resources / text_tank.name
        if installed_text.is_file() and sha256_file(installed_text) == files[text_tank.name]["target_sha256"]:
            print("한국어 패치 B102가 이미 정상 설치되어 있습니다.")
            return 0
        shutil.copy2(text_tank, installed_text)
        print(f"누락된 텍스트 탱크를 복구했습니다: {installed_text}")
        return 0

    if any(state == "patched" for state in states.values()):
        raise SystemExit("두 로직 파일의 설치 상태가 서로 다릅니다. 원본 두 파일을 함께 복원하세요.")

    game_root = resources.parent
    backup_root = game_root / "KoreanPatchBackups"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_root / f"before_B102_{timestamp}"

    try:
        with tempfile.TemporaryDirectory(prefix="u5k_patch_", dir=game_root) as temp_name:
            temp_dir = Path(temp_name)
            generated: dict[str, Path] = {}
            for name in originals:
                output = temp_dir / name
                delta = PATCH_DIR / files[name]["delta"]
                print(f"생성 및 검증 중: {name}")
                apply_delta(resources / name, delta, output)
                if sha256_file(output) != files[name]["target_sha256"]:
                    raise DeltaError(f"최종 해시 검증 실패: {name}")
                generated[name] = output

            backup_dir.mkdir(parents=True)
            for name in originals:
                shutil.copy2(resources / name, backup_dir / name)
            existing_text = resources / text_tank.name
            if existing_text.exists():
                shutil.copy2(existing_text, backup_dir / text_tank.name)

            for name in originals:
                os.replace(generated[name], resources / name)
            shutil.copy2(text_tank, existing_text)
    except (OSError, DeltaError) as exc:
        raise SystemExit(f"설치 실패: {exc}") from exc

    print("\nUltima V: Lazarus 한국어 패치 B102 설치가 완료되었습니다.")
    print(f"백업: {backup_dir}")
    print("게임 실행 전 한국어 폰트 패치도 적용했는지 확인하세요.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n사용자가 취소했습니다.", file=sys.stderr)
        raise SystemExit(130)
