#!/usr/bin/env python3
"""📋 Error Summary — ngumpulin semua error dari monitor & ngasih tau lo."""
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from error_log import ErrorLog

STATE_FILE = os.path.expanduser("~/.hermes/scripts/.error_summary_state.json")
CACHE_FILE = "/root/projects/bounty-output/error_summary_report.txt"
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

LOGBACK_JAM = 24


def main(all_flag=False, clear_flag=False):
    if clear_flag:
        ErrorLog.clear_old(14)
        print("✅ Error log dibersihkan (yang lebih dari 14 hari dihapus)")
        return

    entries = ErrorLog.get_recent(200)
    if not entries:
        _simpan_cache(None)
        print("✅ **Error Log:** Bersih — semua monitor jalan normal.")
        return

    # Filter yang baru sejak check terakhir
    last_check = None
    if os.path.exists(STATE_FILE) and not all_flag:
        try:
            with open(STATE_FILE) as f:
                last_check = json.load(f).get("last_check_ts")
        except:
            pass

    cutoff = last_check or (datetime.now() - timedelta(hours=LOGBACK_JAM)).strftime("%Y-%m-%d %H:%M:%S")
    baru = [e for e in entries if e["ts"] >= cutoff] if not all_flag else entries

    crit = [e for e in baru if e["level"] == "CRITICAL"]
    errs = [e for e in baru if e["level"] == "ERROR"]
    warns = [e for e in baru if e["level"] == "WARNING"]

    total = len(crit) + len(errs) + len(warns)
    if total == 0 and not all_flag:
        _simpan_cache(None)
        return

    header_icon = "💀" if crit else "🔴" if errs else "🟡"
    if total == 0:
        _simpan_cache(None)
        print("✅ **Error Log:** Bersih — semua monitor jalan normal.")
        return

    # Group by display_name
    by_name = {}
    for e in crit + errs + warns:
        name = e.get("display_name", e.get("script", "?"))
        by_name.setdefault(name, []).append(e)

    lines = []
    lines.append(f"{header_icon} Ada **{total} hal** perlu diperhatikan:\n")

    for name in sorted(by_name.keys()):
        items = by_name[name]
        worst = max(items, key=lambda x: ["INFO", "WARNING", "ERROR", "CRITICAL"].index(x["level"]))
        icon = {"CRITICAL": "💀", "ERROR": "🔴", "WARNING": "🟡"}.get(worst["level"], "🟡")

        for e in items:
            level_icon = {"CRITICAL": "💀", "ERROR": "🔴", "WARNING": "🟡"}.get(e["level"], "🟡")
            lines.append(f"{level_icon} **{e['judul']}**")
            lines.append(f"  _{e.get('detail', '')}_")
            if e.get("saran"):
                lines.append(f"  → {e['saran']}")
            lines.append("")

    lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")

    result = "\n".join(lines)

    # Simpan state
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump({"last_check_ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, f)

    _simpan_cache(result)
    print(result)


def _simpan_cache(content):
    try:
        with open(CACHE_FILE, "w") as f:
            if content:
                f.write(content)
            else:
                f.write(f"✅ Error Log bersih.\n🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
    except OSError:
        pass


if __name__ == "__main__":
    all_flag = "--all" in sys.argv
    clear_flag = "--clear" in sys.argv
    try:
        main(all_flag=all_flag, clear_flag=clear_flag)
    except Exception:
        print("🔴 Gagal bikin laporan error — script bermasalah")
