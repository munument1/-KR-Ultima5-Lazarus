#!/usr/bin/env python3
"""Generate a U5K delta. Intended for maintainers, not end users."""

from __future__ import annotations

import argparse
from pathlib import Path

from u5k_delta import build_delta, read_delta_metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Unmodified source file")
    parser.add_argument("target", type=Path, help="Desired patched file")
    parser.add_argument("output", type=Path, help="Delta output path")
    args = parser.parse_args()

    build_delta(args.source, args.target, args.output)
    metadata = read_delta_metadata(args.output)
    print(f"Created: {args.output}")
    print(f"Source SHA-256: {metadata['source_sha256']}")
    print(f"Target SHA-256: {metadata['target_sha256']}")
    print(f"Delta bytes: {args.output.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
