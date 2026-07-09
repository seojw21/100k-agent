#!/usr/bin/env python3
"""Keep only the newest N sections in decisions.md; append the rest to decisions_archive.md.

Non-destructive: writes a timestamped .bak next to decisions.md.

Usage:
  python3 scripts/slim_decisions_md.py
  python3 scripts/slim_decisions_md.py --keep 18
  python3 scripts/slim_decisions_md.py --path "/Users/seojeong-won/reaper-brain/_company/_shared/decisions.md"
"""
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

DEFAULT_PATHS = [
    Path("/Users/seojeong-won/reaper-brain/_company/_shared/decisions.md"),
    Path("/Users/seojeong-won/GEMMA 4/_company/_shared/decisions.md"),
]


def slim_one(path: Path, keep: int) -> None:
    if not path.exists():
        print(f"skip missing: {path}")
        return

    text = path.read_text(encoding="utf-8", errors="ignore")
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    bak = path.with_suffix(path.suffix + f".bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    bak.write_text(text, encoding="utf-8")

    parts = re.split(r"(?=^## \[)", text, flags=re.M)
    sections = [s for s in parts[1:] if s.strip()]
    if len(sections) <= keep:
        move, kept = [], sections
    else:
        move, kept = sections[:-keep], sections[-keep:]

    archive = path.with_name("decisions_archive.md")
    if move:
        block = (
            f"\n\n---\n\n## Archived batch from decisions.md @ {stamp} ({len(move)} sections)\n\n"
            + "".join(move)
        )
        if archive.exists():
            prev = archive.read_text(encoding="utf-8", errors="ignore")
            archive.write_text(prev.rstrip() + block, encoding="utf-8")
        else:
            archive.write_text(
                "# decisions archive\n\n_Older decision log batches._\n" + block,
                encoding="utf-8",
            )

    header = (
        "# 📌 회사 의사결정 로그\n\n"
        "_자가학습이 자동 누적합니다. 잘못된 항목은 직접 삭제하세요._\n\n"
        f"> 컨텍스트 한도 대응: 최근 {len(kept)}개만 유지. 이전 항목은 `decisions_archive.md`.\n"
        f"> slimmed: {stamp}\n\n"
    )
    new_body = header + "".join(kept)
    path.write_text(new_body, encoding="utf-8")
    print(
        f"{path}: kept={len(kept)} archived={len(move)} "
        f"chars {len(text)}->{len(new_body)} bak={bak.name}"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--keep", type=int, default=18, help="sections to keep (default 18)")
    ap.add_argument(
        "--path",
        type=Path,
        action="append",
        default=None,
        help="decisions.md path (repeatable). Default: reaper-brain + GEMMA 4",
    )
    args = ap.parse_args()
    if args.keep < 1:
        raise SystemExit("--keep must be >= 1")
    paths = args.path or DEFAULT_PATHS
    for p in paths:
        slim_one(p, args.keep)


if __name__ == "__main__":
    main()
