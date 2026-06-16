#!/bin/bash
# 🔧 BREACH Error Log — Shell library (for bash monitor scripts)
# Source with: source "$(dirname "$0")/lib/error_log.sh"

ERROR_LOG_FILE="$HOME/.hermes/scripts/.error_log.json"
ERROR_LOG_TMPDIR="${TMPDIR:-/tmp}/breach_error_log"
_ERROR_LOG_SCRIPT=""
_ERROR_LOG_NAME=""
_OK_MSGS=()

error_log_init() {
    _ERROR_LOG_SCRIPT="$1"
    _ERROR_LOG_NAME="$1"
    mkdir -p "$ERROR_LOG_TMPDIR"
    : > "$ERROR_LOG_TMPDIR/entries.json"
    : > "$ERROR_LOG_TMPDIR/ok_msgs.txt"
    echo '[]' > "$ERROR_LOG_TMPDIR/entries.json"
    _OK_MSGS=()
}

error_log__add() {
    local level="$1"
    local judul="$2"
    local detail="$3"
    local saran="${4:-}"
    local ts
    ts=$(date '+%Y-%m-%d %H:%M:%S')

    # Use python with proper argument passing to avoid quoting issues
    python3 - "$ERROR_LOG_TMPDIR/entries.json" "$ts" "$_ERROR_LOG_SCRIPT" "$_ERROR_LOG_NAME" "$level" "$judul" "$detail" "$saran" <<'PYEOF'
import json, sys

f, ts, script, name, level, judul, detail, saran = sys.argv[1:9]

try:
    d = json.load(open(f))
except:
    d = []

d.append({
    "ts": ts,
    "script": script,
    "display_name": name,
    "level": level,
    "judul": judul[:80],
    "detail": detail[:250],
    "saran": saran[:200],
})

json.dump(d, open(f, 'w'))
PYEOF
}

error_log_CRITICAL() { error_log__add "CRITICAL" "$1" "$2" "$3"; }
error_log_ERROR()    { error_log__add "ERROR"    "$1" "$2" "$3"; }
error_log_WARNING()  { error_log__add "WARNING"  "$1" "$2" "$3"; }
error_log_INFO()     { error_log__add "INFO"     "$1" "" ""; }

error_log_ok() {
    _OK_MSGS+=("$*")
    # Write to temp file for python report to read
    printf '%s\n' "$*" >> "$ERROR_LOG_TMPDIR/ok_msgs.txt" 2>/dev/null || true
}

error_log_persist() {
    python3 - "$ERROR_LOG_FILE" "$ERROR_LOG_TMPDIR/entries.json" <<'PYEOF'
import json, os, sys

main_f, tmp_f = sys.argv[1], sys.argv[2]

main = []
if os.path.exists(main_f):
    try: main = json.load(open(main_f))
    except: main = []

try: tmp = json.load(open(tmp_f))
except: tmp = []

if not tmp:
    exit(0)

main.extend(tmp)
if len(main) > 500:
    main = main[-500:]

os.makedirs(os.path.dirname(main_f), exist_ok=True)
json.dump(main, open(main_f, 'w'), indent=2)
PYEOF
}

error_log_report() {
    python3 - "$ERROR_LOG_TMPDIR/entries.json" "$_ERROR_LOG_NAME" <<'PYEOF'
import json, sys
from datetime import datetime

f, display_name = sys.argv[1], sys.argv[2]

try:
    entries = json.load(open(f))
except:
    exit(0)

# Read OK messages from a temp file
ok_file = f.replace("entries.json", "ok_msgs.txt")
ok_items = []
try:
    with open(ok_file) as of:
        ok_items = [l.strip() for l in of if l.strip()]
except:
    pass

has_crit = any(e["level"] == "CRITICAL" for e in entries)
has_err  = any(e["level"] == "ERROR" for e in entries)
has_warn = any(e["level"] == "WARNING" for e in entries)
has_bad  = has_crit or has_err or has_warn

lines = []

if not has_bad:
    if not ok_items:
        exit(0)
    lines.append(f"✅ **{display_name}**")
    lines.append("")
    for msg in ok_items:
        lines.append(f"✅ {msg}")
    lines.append("")
    lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
    print("\n".join(lines))
    exit(0)

header_icon = "💀" if has_crit else "🔴" if has_err else "🟡"
lines.append(f"{header_icon} **{display_name}**")
lines.append("")

for level, icon in [("CRITICAL", "💀"), ("ERROR", "🔴"), ("WARNING", "🟡")]:
    for e in entries:
        if e["level"] != level:
            continue
        lines.append(f"{icon} **{e['judul']}**")
        if e.get("detail"):
            lines.append(f"  {e['detail']}")
        if e.get("saran"):
            lines.append(f"  → {e['saran']}")
        lines.append("")

for msg in ok_items:
    lines.append(f"✅ {msg}")
if ok_items:
    lines.append("")

lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
print("\n".join(lines))
PYEOF
}
