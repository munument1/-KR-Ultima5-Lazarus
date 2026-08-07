#!/usr/bin/env python3
"""Build an Ultima V: Lazarus Korean font test from a user's Dungeon Siege Korean resources.

This script DOES NOT contain or download proprietary Dungeon Siege files.
It patches an existing Korean Language.dsres in place (to a new output file)
so Lazarus' dialogue font key, b_gui_fnt_20p_laztalk, uses a Windows Korean font.
"""

from __future__ import annotations

import argparse
import shutil
import struct
import sys
import zlib
from pathlib import Path

TARGET_RESOURCE = b"global_settings.gas"
SOURCE_FONT_KEY = b"b_gui_fnt_20p_copperplate-light"
TARGET_FONT_KEY = b"b_gui_fnt_20p_laztalk"
DEFAULT_FONT = "굴림"
DEFAULT_SIZE = 18


def u16(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def u32(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def align4(value: int) -> int:
    return (value + 3) & ~3


def locate_resource_entry(data: bytearray, name: bytes) -> tuple[int, int]:
    positions: list[int] = []
    start = 0
    while True:
        pos = data.find(name, start)
        if pos < 0:
            break
        positions.append(pos)
        start = pos + 1

    for name_pos in positions:
        # FileEntry fields before filename:
        # parent(4), size(4), data offset(4), crc(4), FILETIME(8),
        # format(2), flags(2), filename length(2) = 30 bytes.
        entry_start = name_pos - 30
        if entry_start < 0:
            continue
        if u16(data, entry_start + 28) != len(name):
            continue
        if bytes(data[name_pos : name_pos + len(name)]) != name:
            continue
        return entry_start, name_pos

    raise RuntimeError(f"Could not locate a valid Tank FileEntry for {name.decode('ascii')}")


def patch_language_dsres(source: Path, destination: Path, font_name: str, font_size: int) -> None:
    data = bytearray(source.read_bytes())

    if data[:8] != b"DSigTank":
        raise RuntimeError("Input is not a Dungeon Siege 1 Tank/DSRES file (missing DSigTank header).")

    entry_start, name_pos = locate_resource_entry(data, TARGET_RESOURCE)

    uncompressed_size = u32(data, entry_start + 4)
    file_data_rel_offset = u32(data, entry_start + 8)
    data_format = u16(data, entry_start + 24)
    filename_len = u16(data, entry_start + 28)

    if data_format != 1:
        raise RuntimeError(f"global_settings.gas is not Zlib-compressed (format={data_format}).")

    compressed_header = align4(name_pos + filename_len + 1)
    compressed_size = u32(data, compressed_header)
    chunk_size = u32(data, compressed_header + 4)

    if not chunk_size or uncompressed_size > chunk_size:
        raise RuntimeError("This script currently supports the normal single-chunk global_settings.gas layout only.")

    chunk_uncompressed = u32(data, compressed_header + 8)
    chunk_compressed = u32(data, compressed_header + 12)
    chunk_extra = u32(data, compressed_header + 16)
    chunk_offset = u32(data, compressed_header + 20)

    if chunk_uncompressed != uncompressed_size:
        raise RuntimeError("Unexpected chunk metadata: uncompressed sizes do not match.")
    if chunk_compressed != compressed_size:
        raise RuntimeError("Unexpected chunk metadata: compressed sizes do not match.")
    if chunk_extra != 0 or chunk_offset != 0:
        raise RuntimeError("Unexpected global_settings.gas chunk layout (extra bytes or nonzero chunk offset).")

    tank_data_offset = u32(data, 0x18)
    resource_offset = tank_data_offset + file_data_rel_offset
    compressed_payload = bytes(data[resource_offset : resource_offset + compressed_size])

    try:
        raw = zlib.decompress(compressed_payload)
    except zlib.error as exc:
        raise RuntimeError(f"Could not decompress global_settings.gas: {exc}") from exc

    if len(raw) != uncompressed_size:
        raise RuntimeError("Decompressed global_settings.gas size does not match Tank metadata.")

    try:
        text = raw.decode("cp949")
    except UnicodeDecodeError as exc:
        raise RuntimeError("global_settings.gas is not CP949-compatible Korean configuration data.") from exc

    source_key = SOURCE_FONT_KEY.decode("ascii")
    target_key = TARGET_FONT_KEY.decode("ascii")

    source_lines = [line for line in text.splitlines() if source_key in line]
    if len(source_lines) != 1:
        raise RuntimeError(
            f"Expected exactly one {source_key} mapping in global_settings.gas, found {len(source_lines)}."
        )

    old_line = source_lines[0]
    indent = old_line[: len(old_line) - len(old_line.lstrip())]
    new_line = f'{indent}{target_key} = "{font_name},{font_size}";'
    patched_text = text.replace(old_line, new_line, 1)
    patched_raw = patched_text.encode("cp949")

    new_compressed = zlib.compress(patched_raw, 9)

    # Patch the existing Tank data slot without rebuilding the whole archive.
    # The replacement therefore must fit in the original compressed allocation.
    if len(new_compressed) > compressed_size:
        raise RuntimeError(
            f"Patched global_settings.gas is too large for the existing Tank slot "
            f"({len(new_compressed)} > {compressed_size} bytes). Try a shorter Windows font name."
        )

    data[resource_offset : resource_offset + len(new_compressed)] = new_compressed
    tail_start = resource_offset + len(new_compressed)
    tail_end = resource_offset + compressed_size
    data[tail_start:tail_end] = b"\x00" * (tail_end - tail_start)

    # Update resource/chunk sizes.
    struct.pack_into("<I", data, entry_start + 4, len(patched_raw))
    struct.pack_into("<I", data, compressed_header, len(new_compressed))
    struct.pack_into("<I", data, compressed_header + 8, len(patched_raw))
    struct.pack_into("<I", data, compressed_header + 12, len(new_compressed))

    # Zero stale CRCs. Dungeon Siege Tank treats CRC 0 as "not important/not computed".
    struct.pack_into("<I", data, entry_start + 12, 0)
    struct.pack_into("<I", data, 0x50, 0)  # index CRC
    struct.pack_into("<I", data, 0x54, 0)  # data CRC

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)

    # Verify the written resource can be decompressed again and contains the new mapping.
    check = destination.read_bytes()
    new_size = u32(check, compressed_header)
    check_raw = zlib.decompress(check[resource_offset : resource_offset + new_size])
    check_text = check_raw.decode("cp949")
    expected = f'{target_key} = "{font_name},{font_size}";'
    if expected not in check_text:
        raise RuntimeError("Post-write verification failed: Lazarus font mapping was not found.")

    print(f"Patched: {destination}")
    print(f"Mapping: {expected}")
    print(f"Compressed global_settings.gas: {compressed_size} -> {new_size} bytes")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an Ultima V: Lazarus Korean dialogue-font test from Korean Dungeon Siege resources."
    )
    parser.add_argument("language_dsres", type=Path, help="Path to the Korean Resources/Language.dsres")
    parser.add_argument(
        "--language-dll",
        type=Path,
        default=None,
        help="Optional path to Korean Language.dll; copied into the output folder if supplied.",
    )
    parser.add_argument("--font", default=DEFAULT_FONT, help=f"Installed Windows font family (default: {DEFAULT_FONT})")
    parser.add_argument("--size", type=int, default=DEFAULT_SIZE, help=f"Font size (default: {DEFAULT_SIZE})")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("U5L_Korean_Font_Test"),
        help="Output folder (default: U5L_Korean_Font_Test)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.language_dsres.is_file():
        print(f"ERROR: Language.dsres not found: {args.language_dsres}", file=sys.stderr)
        return 2
    if args.language_dll is not None and not args.language_dll.is_file():
        print(f"ERROR: Language.dll not found: {args.language_dll}", file=sys.stderr)
        return 2
    if args.size <= 0:
        print("ERROR: --size must be greater than zero.", file=sys.stderr)
        return 2

    output_dsres = args.output / "Resources" / "Language.dsres"
    patch_language_dsres(args.language_dsres, output_dsres, args.font, args.size)

    if args.language_dll is not None:
        args.output.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.language_dll, args.output / "Language.dll")
        print(f"Copied: {args.output / 'Language.dll'}")

    print("Done. Back up your original files before copying the generated test files into Dungeon Siege.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
