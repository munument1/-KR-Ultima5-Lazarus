#!/usr/bin/env python3
"""
Dungeon Siege 1 Tank (.dsres/.dsmap/.dsm) template-based extractor/repacker.

Purpose
-------
- Inspect/list/extract DS1 Tank archives.
- Repack an existing Tank using the original archive as a template.
- Unchanged resources keep their original stored/compressed bytes and metadata.
- Only replacement files are recompressed/rebuilt.

This is intentionally conservative and aimed at Lazarus logic-resource patching.
It supports RAW and ZLIB resources. LZO resources can be preserved unchanged,
but replacing an LZO resource is refused.

Format references:
  glampert/reverse-engineering-dungeon-siege
  source/siege/tank_file.hpp
  source/siege/tank_file_reader.cpp

WARNING
-------
Always test the produced Tank in DungeonSiege.exe. Structural round-trip checks
are useful, but the game executable is the final compatibility test.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import math
import os
from pathlib import Path, PurePosixPath
import struct
import sys
import zlib
from typing import Dict, List, Optional, Tuple

MAGIC = b"DSigTank"
FMT_RAW = 0
FMT_ZLIB = 1
FMT_LZO = 2
INVALID_CRC = 0
DEFAULT_EXTRA = 16


def u16(buf: bytes, off: int) -> int:
    return struct.unpack_from("<H", buf, off)[0]


def u32(buf: bytes, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def p16(v: int) -> bytes:
    return struct.pack("<H", v)


def p32(v: int) -> bytes:
    return struct.pack("<I", v)


def align_up(v: int, a: int) -> int:
    return (v + a - 1) // a * a


def encode_nstring(raw_name: bytes) -> bytes:
    if len(raw_name) > 0xFFFF:
        raise ValueError("NString too long")
    out = bytearray()
    out += p16(len(raw_name))
    out += raw_name
    out += b"\x00"
    while len(out) % 4:
        out += b"\x00"
    return bytes(out)


def read_nstring(buf: bytes, pos: int) -> Tuple[bytes, int]:
    n = u16(buf, pos)
    start = pos + 2
    end = start + n
    raw = buf[start:end]
    pos = align_up(end + 1, 4)
    return raw, pos


@dataclasses.dataclass
class Chunk:
    uncompressed_size: int
    compressed_size: int
    extra_bytes: int
    offset: int


@dataclasses.dataclass
class FileEntry:
    index: int
    entry_offset: int  # relative to FileSet base
    parent_offset: int  # relative to DirSet base
    size: int
    data_offset: int  # relative to data section
    crc32: int
    filetime: bytes
    fmt: int
    flags: int
    name_raw: bytes
    compressed_size: int = 0
    chunk_size: int = 0
    chunks: List[Chunk] = dataclasses.field(default_factory=list)
    full_path: str = ""

    @property
    def name(self) -> str:
        return self.name_raw.decode("latin1")


@dataclasses.dataclass
class DirEntry:
    index: int
    entry_offset: int  # relative to DirSet base
    parent_offset: int
    child_count: int
    filetime: bytes
    name_raw: bytes
    child_offsets: List[int]
    child_patch_positions: List[int]  # relative to DirSet blob
    full_path: str = ""

    @property
    def name(self) -> str:
        return self.name_raw.decode("latin1")


class Tank:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.buf = self.path.read_bytes()
        if self.buf[:8] != MAGIC:
            raise ValueError(f"Not a DS1 Tank: {self.path}")

        self.header_version = u32(self.buf, 8)
        self.dirset_offset = u32(self.buf, 12)
        self.fileset_offset = u32(self.buf, 16)
        self.index_size = u32(self.buf, 20)
        self.data_offset = u32(self.buf, 24)

        if not (0 < self.data_offset <= self.dirset_offset <= self.fileset_offset <= len(self.buf)):
            raise ValueError("Invalid Tank section offsets")

        self.header_blob = self.buf[: self.data_offset]
        self.dirset_blob = bytearray(self.buf[self.dirset_offset : self.fileset_offset])
        self.dirset_len = len(self.dirset_blob)

        self.dirs = self._parse_dirs()
        self.files = self._parse_files()
        self._build_paths()
        self._file_by_path = {f.full_path.lower(): f for f in self.files}

    def _parse_dirs(self) -> List[DirEntry]:
        base = self.dirset_offset
        n = u32(self.buf, base)
        offs = [u32(self.buf, base + 4 + i * 4) for i in range(n)]
        result: List[DirEntry] = []
        for i, rel in enumerate(offs):
            p = base + rel
            parent = u32(self.buf, p)
            count = u32(self.buf, p + 4)
            filetime = self.buf[p + 8 : p + 16]
            name_raw, p2 = read_nstring(self.buf, p + 16)
            children = []
            patch_positions = []
            for c in range(count):
                pos = p2 + c * 4
                children.append(u32(self.buf, pos))
                patch_positions.append(pos - base)
            result.append(
                DirEntry(i, rel, parent, count, filetime, name_raw, children, patch_positions)
            )
        return result

    def _parse_files(self) -> List[FileEntry]:
        base = self.fileset_offset
        n = u32(self.buf, base)
        offs = [u32(self.buf, base + 4 + i * 4) for i in range(n)]
        result: List[FileEntry] = []
        for i, rel in enumerate(offs):
            p = base + rel
            parent, size, data_off, crc = struct.unpack_from("<IIII", self.buf, p)
            filetime = self.buf[p + 16 : p + 24]
            fmt, flags = struct.unpack_from("<HH", self.buf, p + 24)
            name_raw, p2 = read_nstring(self.buf, p + 28)
            fe = FileEntry(i, rel, parent, size, data_off, crc, filetime, fmt, flags, name_raw)
            if fmt != FMT_RAW and size != 0:
                fe.compressed_size = u32(self.buf, p2)
                fe.chunk_size = u32(self.buf, p2 + 4)
                if fe.chunk_size == 0:
                    raise ValueError(f"Compressed file has chunk_size=0: {fe.name}")
                num_chunks = math.ceil(size / fe.chunk_size)
                q = p2 + 8
                for _ in range(num_chunks):
                    us, cs, ex, co = struct.unpack_from("<IIII", self.buf, q)
                    q += 16
                    fe.chunks.append(Chunk(us, cs, ex, co))
            result.append(fe)
        return result

    def _build_paths(self) -> None:
        dir_by_off = {d.entry_offset: d for d in self.dirs}

        def dir_path(d: DirEntry) -> str:
            if d.full_path:
                return d.full_path
            if d.parent_offset == 0:
                d.full_path = ""
                return ""
            parent = dir_by_off.get(d.parent_offset)
            if parent is None:
                raise ValueError(f"Orphan directory: {d.name}")
            pp = dir_path(parent)
            d.full_path = f"{pp}/{d.name}" if pp else d.name
            return d.full_path

        for d in self.dirs:
            dir_path(d)

        for f in self.files:
            if f.parent_offset == 0:
                f.full_path = f.name
            else:
                parent = dir_by_off.get(f.parent_offset)
                if parent is None:
                    raise ValueError(f"Orphan file: {f.name}")
                pp = dir_path(parent)
                f.full_path = f"{pp}/{f.name}" if pp else f.name

    def stored_blob(self, fe: FileEntry) -> bytes:
        if fe.fmt == FMT_RAW:
            n = fe.size
        else:
            n = fe.compressed_size
        start = self.data_offset + fe.data_offset
        return self.buf[start : start + n]

    def extract_bytes(self, fe: FileEntry) -> bytes:
        if fe.size == 0:
            return b""
        start = self.data_offset + fe.data_offset
        if fe.fmt == FMT_RAW:
            return self.buf[start : start + fe.size]
        if fe.fmt == FMT_LZO:
            raise NotImplementedError(f"LZO extraction not implemented: {fe.full_path}")
        if fe.fmt != FMT_ZLIB:
            raise ValueError(f"Unknown format {fe.fmt}: {fe.full_path}")

        out = bytearray()
        for ch in fe.chunks:
            cp = start + ch.offset
            if ch.uncompressed_size == ch.compressed_size and ch.extra_bytes == 0:
                out += self.buf[cp : cp + ch.uncompressed_size]
                continue
            comp = self.buf[cp : cp + ch.compressed_size]
            dec = zlib.decompress(comp)
            expected_dec = ch.uncompressed_size - ch.extra_bytes
            if len(dec) != expected_dec:
                raise ValueError(
                    f"Bad zlib chunk length {fe.full_path}: got {len(dec)}, expected {expected_dec}"
                )
            out += dec
            if ch.extra_bytes:
                out += self.buf[
                    cp + ch.compressed_size : cp + ch.compressed_size + ch.extra_bytes
                ]
        if len(out) != fe.size:
            raise ValueError(f"Extracted size mismatch {fe.full_path}: {len(out)} != {fe.size}")
        return bytes(out)

    def list(self) -> None:
        print(f"Tank: {self.path}")
        print(f"header_version = 0x{self.header_version:08X}")
        print(f"data_offset    = 0x{self.data_offset:X}")
        print(f"dirset_offset  = 0x{self.dirset_offset:X}")
        print(f"fileset_offset = 0x{self.fileset_offset:X}")
        print(f"dirs={len(self.dirs)} files={len(self.files)}")
        for f in self.files:
            fmt = {FMT_RAW: "raw", FMT_ZLIB: "zlib", FMT_LZO: "lzo"}.get(f.fmt, str(f.fmt))
            print(f"{fmt:4} {f.size:9} {f.full_path}")

    def extract_all(self, out_dir: Path) -> None:
        out_dir = Path(out_dir)
        for i, fe in enumerate(self.files, 1):
            rel = PurePosixPath(fe.full_path)
            dest = out_dir.joinpath(*rel.parts)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(self.extract_bytes(fe))
            if i % 100 == 0 or i == len(self.files):
                print(f"extract {i}/{len(self.files)}")


def compress_zlib_resource(data: bytes, chunk_size: int) -> Tuple[bytes, List[Chunk]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    blob = bytearray()
    chunks: List[Chunk] = []
    if not data:
        return b"", chunks

    n = math.ceil(len(data) / chunk_size)
    for i in range(n):
        chunk = data[i * chunk_size : (i + 1) * chunk_size]
        is_last = i == n - 1

        # GPG/Lazarus convention seen in logic tanks:
        # non-final full chunks keep the last 16 bytes raw as extraBytes.
        extra = DEFAULT_EXTRA if (not is_last and len(chunk) == chunk_size) else 0
        body = chunk[:-extra] if extra else chunk
        tail = chunk[-extra:] if extra else b""

        comp = zlib.compress(body, 9)
        offset = len(blob)

        # If compression loses, store the complete chunk raw.
        # Raw chunks are signaled by uncompressed_size == compressed_size.
        if len(comp) >= len(chunk):
            chunks.append(Chunk(len(chunk), len(chunk), 0, offset))
            blob += chunk
        else:
            chunks.append(Chunk(len(chunk), len(comp), extra, offset))
            blob += comp
            blob += tail

    return bytes(blob), chunks


def serialize_file_entry(
    fe: FileEntry,
    *,
    size: int,
    data_offset: int,
    crc32: int,
    compressed_size: int,
    chunk_size: int,
    chunks: List[Chunk],
) -> bytes:
    out = bytearray()
    out += struct.pack("<IIII", fe.parent_offset, size, data_offset, crc32)
    out += fe.filetime
    out += struct.pack("<HH", fe.fmt, fe.flags)
    out += encode_nstring(fe.name_raw)
    if fe.fmt != FMT_RAW and size != 0:
        out += struct.pack("<II", compressed_size, chunk_size)
        for ch in chunks:
            out += struct.pack(
                "<IIII", ch.uncompressed_size, ch.compressed_size, ch.extra_bytes, ch.offset
            )
    return bytes(out)


def repack(template_path: Path, replacements_dir: Path, output_path: Path) -> None:
    tank = Tank(template_path)
    replacements_dir = Path(replacements_dir)

    # Exact old file-child identifiers in DirSet are relative to DirSet base:
    #   old(FileSet - DirSet) + old FileEntry offset.
    old_child_to_file: Dict[int, int] = {
        tank.dirset_len + fe.entry_offset: fe.index for fe in tank.files
    }

    data = bytearray()
    new_entry_blobs: List[bytes] = []
    new_entry_offsets: List[int] = []
    changed: List[str] = []

    # The FileSet begins with numFiles + offset table.
    next_entry_off = 4 + 4 * len(tank.files)

    for fe in tank.files:
        # Resource data offsets are aligned to 8 bytes relative to data section.
        while len(data) % 8:
            data += b"\x00"
        new_data_off = len(data)

        rel = PurePosixPath(fe.full_path)
        replacement = replacements_dir.joinpath(*rel.parts)

        if replacement.is_file():
            new_bytes = replacement.read_bytes()
            changed.append(fe.full_path)
            new_crc = zlib.crc32(new_bytes) & 0xFFFFFFFF

            if fe.fmt == FMT_RAW:
                stored = new_bytes
                new_chunks: List[Chunk] = []
                new_comp_size = 0
                new_chunk_size = 0
            elif fe.fmt == FMT_ZLIB:
                # Preserve the template's chunk size; Lazarus logic uses 16384.
                new_chunk_size = fe.chunk_size or 16384
                stored, new_chunks = compress_zlib_resource(new_bytes, new_chunk_size)
                new_comp_size = len(stored)
            elif fe.fmt == FMT_LZO:
                raise RuntimeError(
                    f"Refusing to replace LZO resource without an LZO encoder: {fe.full_path}"
                )
            else:
                raise RuntimeError(f"Unknown resource format {fe.fmt}: {fe.full_path}")

            size = len(new_bytes)
            crc = new_crc
            comp_size = new_comp_size
            chunk_size = new_chunk_size
            chunks = new_chunks
        else:
            # Critical conservative behavior: unchanged resources are copied byte-for-byte.
            stored = tank.stored_blob(fe)
            size = fe.size
            crc = fe.crc32
            comp_size = fe.compressed_size
            chunk_size = fe.chunk_size
            chunks = fe.chunks

        data += stored

        entry_blob = serialize_file_entry(
            fe,
            size=size,
            data_offset=new_data_off,
            crc32=crc,
            compressed_size=comp_size,
            chunk_size=chunk_size,
            chunks=chunks,
        )
        new_entry_offsets.append(next_entry_off)
        new_entry_blobs.append(entry_blob)
        next_entry_off += len(entry_blob)

    # Preserve relative 8-byte alignment and GPG's 16-byte pad before DirSet.
    while len(data) % 8:
        data += b"\x00"
    data += b"\x00" * 16

    # Build FileSet.
    fileset = bytearray()
    fileset += p32(len(tank.files))
    for off in new_entry_offsets:
        fileset += p32(off)
    for blob in new_entry_blobs:
        fileset += blob

    # DirSet structure itself is fixed-size because names/counts did not change.
    # Patch every file child pointer to the newly sized FileEntry position.
    dirset = bytearray(tank.dirset_blob)
    for d in tank.dirs:
        for child_value, patch_pos in zip(d.child_offsets, d.child_patch_positions):
            fi = old_child_to_file.get(child_value)
            if fi is None:
                # Directory child: relative DirSet offset stays unchanged.
                continue
            new_child_value = tank.dirset_len + new_entry_offsets[fi]
            struct.pack_into("<I", dirset, patch_pos, new_child_value)

    new_dirset_off = tank.data_offset + len(data)
    new_fileset_off = new_dirset_off + len(dirset)
    new_index_size = len(dirset) + len(fileset)

    header = bytearray(tank.header_blob)
    struct.pack_into("<I", header, 12, new_dirset_off)
    struct.pack_into("<I", header, 16, new_fileset_off)
    struct.pack_into("<I", header, 20, new_index_size)

    # Header fields at offsets 80/84 are index/data CRC32 in v1.0.x.
    # 0 is the documented InvalidChecksum / "not important" value.
    # This avoids claiming a checksum we have not reproduced exactly.
    if len(header) >= 88 and changed:
        struct.pack_into("<I", header, 80, INVALID_CRC)
        struct.pack_into("<I", header, 84, INVALID_CRC)

    output = bytes(header) + bytes(data) + bytes(dirset) + bytes(fileset)
    Path(output_path).write_bytes(output)

    print(f"template : {template_path}")
    print(f"output   : {output_path}")
    print(f"changed  : {len(changed)} resources")
    print(f"files    : {len(tank.files)}")
    print(f"size     : {len(output):,} bytes")
    if changed:
        for p in changed[:20]:
            print(f"  + {p}")
        if len(changed) > 20:
            print(f"  ... +{len(changed)-20} more")

    # Self-check: parse output and verify every resource can be extracted.
    verify = Tank(output_path)
    if len(verify.files) != len(tank.files):
        raise RuntimeError("Verification failed: file count changed")

    # Verify replacement bytes and unchanged resources by uncompressed content.
    for i, (old_fe, new_fe) in enumerate(zip(tank.files, verify.files), 1):
        rel = PurePosixPath(old_fe.full_path)
        replacement = replacements_dir.joinpath(*rel.parts)
        got = verify.extract_bytes(new_fe)
        expected = replacement.read_bytes() if replacement.is_file() else tank.extract_bytes(old_fe)
        if got != expected:
            raise RuntimeError(f"Verification mismatch: {old_fe.full_path}")
        if i % 200 == 0 or i == len(tank.files):
            print(f"verify  {i}/{len(tank.files)}")

    print("SELF-CHECK OK")


def cmd_info(args: argparse.Namespace) -> None:
    Tank(Path(args.tank)).list()


def cmd_extract(args: argparse.Namespace) -> None:
    Tank(Path(args.tank)).extract_all(Path(args.out))


def cmd_repack(args: argparse.Namespace) -> None:
    repack(Path(args.template), Path(args.replacements), Path(args.output))


def main() -> int:
    ap = argparse.ArgumentParser(description="Dungeon Siege 1 Tank extractor/repacker")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("info", help="list Tank contents")
    p.add_argument("tank")
    p.set_defaults(func=cmd_info)

    p = sub.add_parser("extract", help="extract all resources")
    p.add_argument("tank")
    p.add_argument("out")
    p.set_defaults(func=cmd_extract)

    p = sub.add_parser("repack", help="repack template, replacing files found under a directory")
    p.add_argument("template")
    p.add_argument("replacements")
    p.add_argument("output")
    p.set_defaults(func=cmd_repack)

    args = ap.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
