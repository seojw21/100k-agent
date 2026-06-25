#!/usr/bin/env python3
import os

BASE_DIR = "/Users/seojeong-won/GEMMA 4"
DECISIONS_PATH = os.path.join(BASE_DIR, "_company", "_shared", "decisions.md")
DECISIONS_ARCHIVE_PATH = os.path.join(BASE_DIR, "_company", "_shared", "decisions_archive.md")

CEO_MEMORY_PATH = os.path.join(BASE_DIR, "_company", "_agents", "ceo", "memory.md")
CEO_MEMORY_ARCHIVE_PATH = os.path.join(BASE_DIR, "_company", "_agents", "ceo", "memory_archive.md")

def archive_decisions():
    if not os.path.exists(DECISIONS_PATH):
        print(f"Skipping decisions archiving: {DECISIONS_PATH} not found.")
        return

    print("Archiving decisions.md...")
    with open(DECISIONS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Save to archive
    with open(DECISIONS_ARCHIVE_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved decisions archive to: {DECISIONS_ARCHIVE_PATH}")

    # Process new content: keep header + entries from 2026-06-15 onwards
    lines = content.splitlines()
    header = lines[:4]
    
    recent_lines = []
    keep = False
    for line in lines[4:]:
        if line.startswith("## [2026-06-15]"):
            keep = True
        if keep:
            recent_lines.append(line)

    new_content = "\n".join(header) + "\n\n"
    new_content += "[... archived older entries in decisions_archive.md ...]\n\n"
    new_content += "\n".join(recent_lines) + "\n"

    with open(DECISIONS_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated decisions.md (reduced to {len(recent_lines)} lines of recent entries).")


def archive_ceo_memory():
    if not os.path.exists(CEO_MEMORY_PATH):
        print(f"Skipping CEO memory archiving: {CEO_MEMORY_PATH} not found.")
        return

    print("Archiving CEO memory.md...")
    with open(CEO_MEMORY_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Save to archive
    with open(CEO_MEMORY_ARCHIVE_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved CEO memory archive to: {CEO_MEMORY_ARCHIVE_PATH}")

    # Process new content: keep header (first 6 lines) + entries from 2026-06-15 onwards
    lines = content.splitlines()
    header = lines[:6]
    
    recent_lines = []
    keep = False
    for line in lines[6:]:
        if line.startswith("- [2026-06-15]"):
            keep = True
        if keep:
            recent_lines.append(line)

    new_content = "\n".join(header) + "\n"
    new_content += "- [... archived older entries in memory_archive.md ...]\n"
    new_content += "\n".join(recent_lines) + "\n"

    with open(CEO_MEMORY_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Updated CEO memory.md (reduced to {len(recent_lines)} lines of recent entries).")

if __name__ == "__main__":
    archive_decisions()
    archive_ceo_memory()
