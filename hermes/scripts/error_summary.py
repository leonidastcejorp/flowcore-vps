#!/usr/bin/env python3
"""
📋 LogDesk — ringkasan error dari semua monitor. Aman = silent.
"""
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from error_log import ErrorLog
from telegram_ui import TelegramMessage

STATE_FILE = os.path.expanduser("~/.hermes/scripts/.error_summary_state.json")
CACHE_FILE = "/root/projects/bounty-output/error_summary_report.txt"
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

LOGBACK_JAM = 24


def main(all_flag=False, clear_flag=False):
    if clear_flag:
        ErrorLog.clear_old(14)
        _simpan_cache(None)
        print("✅ Error log dibersihkan (yang lebih dari 14 hari dihapus)")
        return

    entries = ErrorLog.get_recent(200)
    if not entries:
        _simpan_cache(None)
        return

    last_check = None
    if os.path.exists(STATE_FILE) and not all_flag:
        try:
            with open(STATE_FILE) as f:
                last_check = json.load(f).get("last_check_ts")
        except Exception:
            pass

    cutoff = last_check or (datetime.now() - timedelta(hours=LOGBACK_JAM)).strftime("%Y-%m-%d %H:%M:%S")
    baru = [e for e in entries if e["ts"] >= cutoff] if not all_flag else entries

    crit = [e for e in baru if e["level"] == "CRITICAL"]
    errs = [e for e in baru if e["level"] == "ERROR"]
    warns = [e for e in baru if e["level"] == "WARNING"]
    total = len(crit) + len(errs) + len(warns)

    # Simpan state dulu
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"last_check_ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, f)

    if total == 0:
        _simpan_cache(None)
        return

    level = "CRITICAL" if crit else "ERROR" if errs else "WARNING"
    msg = TelegramMessage("📋 LogDesk", "", level=level)

    msg.add_text(f"Ada **{total} masalah** yang perlu diperhatikan:\n")

    # Tabel ringkasan
    msg.add_table(
        ["Level", "Jumlah", "Indikator"],
        [
            ["CRITICAL", str(len(crit)), "💀" if crit else "-"],
            ["ERROR", str(len(errs)), "🔴" if errs else "-"],
            ["WARNING", str(len(warns)), "🟡" if warns else "-"],
        ],
    )

    # Detail per entry
    for e in crit + errs + warns:
        icon = "💀" if e["level"] == "CRITICAL" else "🔴" if e["level"] == "ERROR" else "🟡"
        msg.add_text(f"{icon} **{e.get('display_name', e.get('script', '?'))}**  \u00b7  `{e['ts']}`")
        msg.add_text(f"`{e['judul']}`")
        if e.get("detail"):
            msg.add_text(f"  {e['detail'][:120]}")
        if e.get("saran"):
            msg.add_text(f"  → {e['saran'][:120]}")

    result = msg.render()
    _simpan_cache(result)
    print(result)


def _simpan_cache(content):
    try:
        with open(CACHE_FILE, "w") as f:
            if content:
                f.write(content)
            else:
                f.write("✅ Error Log bersih.")
    except OSError:
        pass


if __name__ == "__main__":
    all_flag = "--all" in sys.argv
    clear_flag = "--clear" in sys.argv
    try:
        main(all_flag=all_flag, clear_flag=clear_flag)
    except Exception:
        print("🔴 Gagal bikin laporan error — script bermasalah")
