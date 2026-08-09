#!/usr/bin/env python3
"""Small, dependency-free binary delta format used by the U5 Lazarus patch."""

from __future__ import annotations

import hashlib
import io
import struct
import zlib
from pathlib import Path


MAGIC = b"U5KDELTA"
HEADER = struct.Struct("<8sQQ32s32s")
COPY = struct.Struct("<QI")
LENGTH = struct.Struct("<I")


class DeltaError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def build_delta(
    source_path: Path,
    target_path: Path,
    output_path: Path,
    *,
    block_size: int = 32,
    stride: int = 4,
    max_candidates: int = 8,
) -> None:
    """Create a compressed COPY/ADD delta from source_path to target_path."""
    source = source_path.read_bytes()
    target = target_path.read_bytes()
    if block_size < 8 or stride < 1:
        raise ValueError("block_size must be >= 8 and stride must be >= 1")

    index: dict[bytes, list[int]] = {}
    final_start = len(source) - block_size
    for offset in range(0, final_start + 1, stride):
        key = source[offset : offset + block_size]
        positions = index.get(key)
        if positions is None:
            index[key] = [offset]
        elif len(positions) < max_candidates:
            positions.append(offset)

    operations = io.BytesIO()
    add_buffer = bytearray()

    def flush_add() -> None:
        if not add_buffer:
            return
        operations.write(b"A")
        operations.write(LENGTH.pack(len(add_buffer)))
        operations.write(add_buffer)
        add_buffer.clear()

    position = 0
    target_limit = len(target)
    while position < target_limit:
        candidates = None
        if position + block_size <= target_limit:
            candidates = index.get(target[position : position + block_size])

        if not candidates:
            add_buffer.append(target[position])
            position += 1
            continue

        best_offset = candidates[0]
        best_length = block_size
        for source_offset in candidates:
            length = block_size
            max_length = min(len(source) - source_offset, target_limit - position)
            while length < max_length and source[source_offset + length] == target[position + length]:
                length += 1
            if length > best_length:
                best_offset = source_offset
                best_length = length

        flush_add()
        remaining = best_length
        copy_offset = best_offset
        while remaining:
            chunk_length = min(remaining, 0xFFFFFFFF)
            operations.write(b"C")
            operations.write(COPY.pack(copy_offset, chunk_length))
            copy_offset += chunk_length
            remaining -= chunk_length
        position += best_length

    flush_add()
    compressed = zlib.compress(operations.getvalue(), level=9)
    header = HEADER.pack(
        MAGIC,
        len(source),
        len(target),
        sha256_bytes(source),
        sha256_bytes(target),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(header + compressed)


def read_delta_metadata(delta_path: Path) -> dict[str, object]:
    raw = delta_path.read_bytes()
    if len(raw) < HEADER.size:
        raise DeltaError(f"Delta header is truncated: {delta_path}")
    magic, source_size, target_size, source_hash, target_hash = HEADER.unpack_from(raw)
    if magic != MAGIC:
        raise DeltaError(f"Unsupported delta format: {delta_path}")
    return {
        "source_size": source_size,
        "target_size": target_size,
        "source_sha256": source_hash.hex().upper(),
        "target_sha256": target_hash.hex().upper(),
    }


def apply_delta(source_path: Path, delta_path: Path, output_path: Path) -> None:
    source = source_path.read_bytes()
    raw = delta_path.read_bytes()
    if len(raw) < HEADER.size:
        raise DeltaError(f"Delta header is truncated: {delta_path}")

    magic, source_size, target_size, source_hash, target_hash = HEADER.unpack_from(raw)
    if magic != MAGIC:
        raise DeltaError(f"Unsupported delta format: {delta_path}")
    if len(source) != source_size or sha256_bytes(source) != source_hash:
        raise DeltaError(
            f"Source file does not match this patch: {source_path.name} "
            f"(SHA-256 {sha256_bytes(source).hex().upper()})"
        )

    try:
        operations = memoryview(zlib.decompress(raw[HEADER.size :]))
    except zlib.error as exc:
        raise DeltaError(f"Delta payload is corrupt: {delta_path}") from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    written = 0
    cursor = 0
    with output_path.open("wb") as output:
        while cursor < len(operations):
            opcode = bytes(operations[cursor : cursor + 1])
            cursor += 1
            if opcode == b"C":
                if cursor + COPY.size > len(operations):
                    raise DeltaError("Truncated COPY operation")
                source_offset, length = COPY.unpack_from(operations, cursor)
                cursor += COPY.size
                end = source_offset + length
                if end > len(source):
                    raise DeltaError("COPY operation exceeds the source file")
                chunk = source[source_offset:end]
            elif opcode == b"A":
                if cursor + LENGTH.size > len(operations):
                    raise DeltaError("Truncated ADD operation")
                (length,) = LENGTH.unpack_from(operations, cursor)
                cursor += LENGTH.size
                end = cursor + length
                if end > len(operations):
                    raise DeltaError("ADD operation exceeds the delta payload")
                chunk = operations[cursor:end]
                cursor = end
            else:
                raise DeltaError(f"Unknown delta opcode at byte {cursor - 1}")

            output.write(chunk)
            digest.update(chunk)
            written += len(chunk)

    if written != target_size or digest.digest() != target_hash:
        output_path.unlink(missing_ok=True)
        raise DeltaError("Patched output failed its size or SHA-256 verification")
