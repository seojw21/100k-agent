#!/usr/bin/env bash
# Re-apply Connect AI Lab context-window patch after extension updates.
# - num_ctx: 8192 -> 32768 (or --ctx N)
# - MAX_CONTEXT_SIZE: 12e3 -> 20e3 (per-file inject budget)
#
# Usage:
#   bash scripts/patch_connect_num_ctx.sh
#   bash scripts/patch_connect_num_ctx.sh --ctx 16384
#   bash scripts/patch_connect_num_ctx.sh --check   # report only
set -euo pipefail

CTX="${CTX:-32768}"
CHECK_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ctx)
      CTX="${2:?}"
      shift 2
      ;;
    --check)
      CHECK_ONLY=1
      shift
      ;;
    -h|--help)
      sed -n '1,12p' "$0"
      exit 0
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if ! [[ "$CTX" =~ ^[0-9]+$ ]] || [[ "$CTX" -lt 2048 ]]; then
  echo "invalid --ctx: $CTX" >&2
  exit 2
fi

# Prefer Antigravity, then VS Code / Cursor style paths
shopt -s nullglob
CANDIDATES=(
  "$HOME/.antigravity-ide/extensions"/connectailab.connect-ai-lab-*/out/extension.js
  "$HOME/.vscode/extensions"/connectailab.connect-ai-lab-*/out/extension.js
  "$HOME/.cursor/extensions"/connectailab.connect-ai-lab-*/out/extension.js
)

if [[ ${#CANDIDATES[@]} -eq 0 ]]; then
  echo "Connect AI Lab extension.js not found under ~/.antigravity-ide|~/.vscode|~/.cursor" >&2
  exit 1
fi

# Newest mtime wins (latest install)
EXT="$(ls -t "${CANDIDATES[@]}" | head -1)"
echo "target: $EXT"

python3 - "$EXT" "$CTX" "$CHECK_ONLY" <<'PY'
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ext = Path(sys.argv[1])
ctx = int(sys.argv[2])
check_only = sys.argv[3] == "1"

raw = ext.read_text(encoding="utf-8", errors="ignore")
n_8192 = len(re.findall(r"num_ctx:\s*8192", raw))
n_target = len(re.findall(rf"num_ctx:\s*{ctx}", raw))
n_any = re.findall(r"num_ctx:\s*(\d+)", raw)
max_m = re.search(r"MAX_CONTEXT_SIZE\s*=\s*([^;]+)", raw)

print(f"num_ctx values found: {sorted(set(n_any))}")
print(f"num_ctx 8192 count: {n_8192}")
print(f"num_ctx {ctx} count: {n_target}")
print(f"MAX_CONTEXT_SIZE: {max_m.group(1) if max_m else 'not found'}")

if check_only:
    ok = n_8192 == 0 and n_target > 0
    print("status:", "OK (patched)" if ok else "NEEDS PATCH")
    sys.exit(0 if ok else 1)

if n_8192 == 0 and n_target > 0:
    # still ensure MAX budget
    text = raw
    changed = False
else:
    bak = ext.with_name(ext.name + f".bak-numctx-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    shutil.copy2(ext, bak)
    print(f"backup: {bak}")
    text = re.sub(r"num_ctx:\s*8192", f"num_ctx: {ctx}", raw)
    # If already some other value, force all num_ctx assignments that look like options defaults
    # Only replace common hardcoded small windows
    text = re.sub(r"num_ctx:\s*(4096|8192|10240)", f"num_ctx: {ctx}", text)
    changed = text != raw

# Raise per-file inject budget so slim decisions.md can be included
if re.search(r"MAX_CONTEXT_SIZE\s*=\s*12e3", text):
    text = re.sub(r"MAX_CONTEXT_SIZE\s*=\s*12e3", "MAX_CONTEXT_SIZE = 20e3", text, count=1)
    changed = True
    print("MAX_CONTEXT_SIZE: 12e3 -> 20e3")
elif max_m and max_m.group(1).strip() == "20e3":
    print("MAX_CONTEXT_SIZE already 20e3")
else:
    print("MAX_CONTEXT_SIZE left as-is")

if not changed and n_8192 == 0:
    print("already patched; no write")
else:
    if n_8192 == 0 and not changed:
        pass
    else:
        if "bak" not in dir() or not bak.exists():
            bak = ext.with_name(ext.name + f".bak-numctx-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            shutil.copy2(ext, bak)
            print(f"backup: {bak}")
        ext.write_text(text, encoding="utf-8")
        print(f"wrote patch num_ctx -> {ctx}")

raw2 = ext.read_text(encoding="utf-8", errors="ignore")
left = len(re.findall(r"num_ctx:\s*8192", raw2))
have = len(re.findall(rf"num_ctx:\s*{ctx}", raw2))
print(f"verify: remaining 8192={left}, {ctx}={have}")
if left:
    print("WARNING: some 8192 sites remain", file=sys.stderr)
    sys.exit(1)
print("OK — Reload Window (or restart Antigravity) to load the patch.")
PY
