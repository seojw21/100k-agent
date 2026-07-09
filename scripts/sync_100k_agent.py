#!/usr/bin/env python3
"""
GEMMA 4 (로컬 두뇌) ↔ 100k-agent (깃허브 두뇌 백업) 동기화

용도:
  - push: GEMMA 4 → 100k-agent 클론에 화이트리스트 복사 후 commit/push
  - pull: 100k-agent → GEMMA 4 로 목표/문서만 안전하게 가져오기
  - status: 차이 요약

사용:
  python3 scripts/sync_100k_agent.py status
  python3 scripts/sync_100k_agent.py push --commit --push
  python3 scripts/sync_100k_agent.py pull --dry-run
  python3 scripts/sync_100k_agent.py push --commit --push --message "sync: weekly brain"

환경 변수:
  GEMMA4_ROOT   기본: 이 스크립트 기준 상위 (GEMMA 4)
  AGENT_ROOT    기본: ~/100k-agent
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_GEMMA = SCRIPT_DIR.parent
DEFAULT_AGENT = Path.home() / "100k-agent"

# GEMMA 4 → 100k-agent (및 pull 시 반대 방향)에 복사할 경로
# rateparse/ whatsapp 제품 코드는 절대 포함하지 않음
SYNC_PATHS: list[str] = [
    "_shared/goals.md",
    "_shared/identity.md",
    "_shared/main_product.md",
    "_shared/decisions.md",
    "_shared/_system.md",
    "_company/_shared/goals.md",
    "_company/_shared/identity.md",
    "_company/_shared/decisions.md",
    "_company/_shared/_system.md",
    "_company/_shared/schedule.md",
    "business/",
    "knowledge/pain_db.json",
    "knowledge/README.md",
    "knowledge/index.json",
    "knowledge/top_ideas.md",
    "knowledge/projects_knowledge_base.md",
    "knowledge/collected_ids.json",
    "knowledge/processed_ids.json",
    "00_Raw/",
    "10_Wiki/",
    "20_Meta/",
    "company_state.json",
    "README.md",
]

# 디렉터리 전체 동기화 시 제외
DIR_EXCLUDE_NAMES = {
    "node_modules",
    ".git",
    ".venv",
    "__pycache__",
    "chroma_db",
    "md_brain",
    "raw_events",
    ".DS_Store",
    "kmong_portfolio",  # 샘플 xlsx/png — 필요 시 수동 복사
}

# pull 시 덮어쓰지 않을 로컬 전용(제품 등) — pull 화이트리스트만 쓰므로 별도 가드
PULL_BLOCK_PREFIXES = (
    "rateparse/",
    "whatsapp-review-saas/",
    "node_modules/",
    ".env",
)


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True, check=check)


def should_skip(rel: Path) -> bool:
    parts = set(rel.parts)
    if parts & DIR_EXCLUDE_NAMES:
        return True
    name = rel.name
    if name.endswith((".log", ".tmp", ".pyc")):
        return True
    if name.endswith(".jsonl") and "pain" not in name:
        return True
    return False


def iter_sync_files(src_root: Path) -> list[Path]:
    files: list[Path] = []
    for entry in SYNC_PATHS:
        p = src_root / entry
        if not p.exists():
            continue
        if p.is_file():
            files.append(p.relative_to(src_root))
            continue
        if p.is_dir():
            for f in p.rglob("*"):
                if not f.is_file():
                    continue
                rel = f.relative_to(src_root)
                if should_skip(rel):
                    continue
                files.append(rel)
    return sorted(set(files))


def copy_file(src: Path, dst: Path, dry_run: bool) -> str:
    if dry_run:
        return "would_copy"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return "copied"


def diff_plan(src_root: Path, dst_root: Path) -> tuple[list[str], list[str], list[str]]:
    """Returns (new, changed, same) relative path strings."""
    new, changed, same = [], [], []
    for rel in iter_sync_files(src_root):
        s, d = src_root / rel, dst_root / rel
        rel_s = str(rel).replace("\\", "/")
        if not d.exists():
            new.append(rel_s)
        elif not filecmp.cmp(s, d, shallow=False):
            changed.append(rel_s)
        else:
            same.append(rel_s)
    return new, changed, same


def apply_sync(src_root: Path, dst_root: Path, dry_run: bool) -> dict:
    new, changed, same = diff_plan(src_root, dst_root)
    actions = []
    for rel in new + changed:
        st = copy_file(src_root / rel, dst_root / rel, dry_run=dry_run)
        actions.append((st, rel))
    return {
        "new": new,
        "changed": changed,
        "same": same,
        "actions": actions,
        "src": str(src_root),
        "dst": str(dst_root),
    }


def git_commit_push(agent_root: Path, message: str, do_push: bool, dry_run: bool) -> None:
    if dry_run:
        print("[dry-run] skip git commit/push")
        return
    run(["git", "add", "-A"], cwd=agent_root)
    st = run(["git", "status", "--porcelain"], cwd=agent_root, check=False)
    if not st.stdout.strip():
        print("Nothing to commit (already in sync).")
        return
    run(["git", "commit", "-m", message], cwd=agent_root)
    print("Committed:", message)
    if do_push:
        run(["git", "push", "origin", "HEAD"], cwd=agent_root)
        print("Pushed to origin.")


def cmd_status(gemma: Path, agent: Path) -> int:
    print(f"GEMMA 4 : {gemma}")
    print(f"100k    : {agent}")
    if not agent.exists():
        print("ERROR: 100k-agent clone missing. git clone https://github.com/seojw21/100k-agent.git ~/100k-agent")
        return 2
    new, changed, same = diff_plan(gemma, agent)
    print(f"\n→ push 방향 (GEMMA → 100k): new={len(new)} changed={len(changed)} same={len(same)}")
    for label, items in (("NEW", new[:20]), ("CHANGED", changed[:20])):
        if items:
            print(f"\n{label}:")
            for x in items:
                print(" ", x)
            if label == "NEW" and len(new) > 20:
                print(f"  ... +{len(new)-20} more")
            if label == "CHANGED" and len(changed) > 20:
                print(f"  ... +{len(changed)-20} more")
    new_p, ch_p, same_p = diff_plan(agent, gemma)
    print(f"\n← pull 방향 (100k → GEMMA): new={len(new_p)} changed={len(ch_p)} same={len(same_p)}")
    return 0


def cmd_push(gemma: Path, agent: Path, dry_run: bool, do_commit: bool, do_push: bool, message: str) -> int:
    if not agent.exists():
        print("ERROR: agent root missing:", agent)
        return 2
    # ensure on main-ish
    result = apply_sync(gemma, agent, dry_run=dry_run)
    print(f"Sync GEMMA → 100k: new={len(result['new'])} changed={len(result['changed'])}")
    for a, rel in result["actions"][:30]:
        print(f"  {a}: {rel}")
    if len(result["actions"]) > 30:
        print(f"  ... +{len(result['actions'])-30} more")
    # refresh OPTIMIZE note stamp
    if not dry_run:
        log = agent / "SYNC_LOG.md"
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        line = f"- {stamp} push from GEMMA 4 (new={len(result['new'])} changed={len(result['changed'])})\n"
        prev = log.read_text(encoding="utf-8") if log.exists() else "# Sync log\n\n"
        log.write_text(prev + line, encoding="utf-8")
    if do_commit:
        git_commit_push(agent, message, do_push=do_push, dry_run=dry_run)
    elif do_push and not dry_run:
        print("Note: --push requires --commit (or commit manually).")
    return 0


def cmd_pull(gemma: Path, agent: Path, dry_run: bool) -> int:
    """Safe pull: only SYNC_PATHS into GEMMA, never product trees."""
    if not agent.exists():
        print("ERROR: agent root missing:", agent)
        return 2
    # Guard: refuse if destination is product-only somehow
    result = apply_sync(agent, gemma, dry_run=dry_run)
    # filter blocked
    blocked = [r for r in result["new"] + result["changed"] if r.startswith(PULL_BLOCK_PREFIXES)]
    if blocked:
        print("ERROR: pull would touch blocked paths:", blocked)
        return 1
    print(f"Sync 100k → GEMMA: new={len(result['new'])} changed={len(result['changed'])}")
    for a, rel in result["actions"][:30]:
        print(f"  {a}: {rel}")
    if not dry_run:
        print("Pulled into GEMMA 4. Review git status in GEMMA 4 if that folder is a git repo.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Sync GEMMA 4 ↔ 100k-agent brain")
    p.add_argument("command", choices=["status", "push", "pull"])
    p.add_argument("--gemma", type=Path, default=Path(os.environ.get("GEMMA4_ROOT", DEFAULT_GEMMA)))
    p.add_argument("--agent", type=Path, default=Path(os.environ.get("AGENT_ROOT", DEFAULT_AGENT)))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--commit", action="store_true", help="push 명령에서 100k-agent에 커밋")
    p.add_argument("--push", action="store_true", help="commit 후 origin push")
    p.add_argument(
        "--message",
        default=None,
        help="commit message",
    )
    args = p.parse_args(argv)

    gemma = args.gemma.expanduser().resolve()
    agent = args.agent.expanduser().resolve()
    if not gemma.is_dir():
        print("ERROR: GEMMA root not found:", gemma)
        return 2

    msg = args.message or f"sync: brain from GEMMA 4 ({datetime.now().strftime('%Y-%m-%d')})"

    if args.command == "status":
        return cmd_status(gemma, agent)
    if args.command == "push":
        return cmd_push(gemma, agent, args.dry_run, args.commit, args.push, msg)
    if args.command == "pull":
        return cmd_pull(gemma, agent, args.dry_run)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
