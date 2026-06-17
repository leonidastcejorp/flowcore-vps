#!/usr/bin/env python3
"""
📈 MemStat — alert RAM & swap. Aman = silent.
"""
import json
import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from error_log import ErrorLog
from telegram_ui import TelegramMessage, progress_bar

STATE_FILE = os.path.expanduser("~/.hermes/scripts/.memory_state.json")
SWAP_WARN_MB = 500
MEM_WARN_PCT = 90

log = ErrorLog("📈 MemStat")


def cek(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.returncode == 0
    except Exception:
        return "", False


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def main():
    raw, ok = cek(["free", "-m"])
    if not ok or not raw:
        log.error("Gagal baca memory", "Perintah free -m error", "Cek manual")
        log.persist()
        return

    try:
        lines = raw.split("\n")
        mem = [c for c in lines if c.startswith("Mem:")][0].split()
        swap = [c for c in lines if c.startswith("Swap:")][0].split()
        mem_total = int(mem[1])
        mem_used = int(mem[2])
        mem_avail = int(mem[6])
        mem_pct = int(mem_used * 100 / mem_total)
        swap_total = int(swap[1])
        swap_used = int(swap[2])
        swap_pct = int(swap_used * 100 / swap_total) if swap_total > 0 else 0
    except Exception:
        log.error("Gagal parse memory", "Format output free -m aneh", "Cek manual")
        log.persist()
        return

    prev = load_state()
    alerts = []

    # RAM kritis
    if mem_pct > MEM_WARN_PCT:
        if not prev.get("ram_critical_warned", False):
            alerts.append(("CRITICAL", "RAM mau habis", f"{mem_pct}% ({mem_avail}MB sisa)", "Tutup program atau restart service"))
            log.critical("RAM kritis", f"{mem_pct}%", "Tutup program")
        prev["ram_critical_warned"] = True
    else:
        prev["ram_critical_warned"] = False

    # Swap tinggi
    if swap_used > SWAP_WARN_MB:
        if not prev.get("swap_warned", False):
            alerts.append(("WARNING", "Swap mulai penuh", f"{swap_used}MB/{swap_total}MB ({swap_pct}%)", "Tutup aplikasi boros atau upgrade RAM"))
            log.warning("Swap tinggi", f"{swap_used}MB/{swap_total}MB", "Tutup aplikasi boros")
        prev["swap_warned"] = True
    else:
        prev["swap_warned"] = False

    # Recovery notif
    if prev.get("ram_critical_prev", False) and mem_pct <= MEM_WARN_PCT:
        alerts.append(("OK", "RAM kembali normal", f"{mem_pct}% ({mem_avail}MB sisa)", ""))
    prev["ram_critical_prev"] = mem_pct > MEM_WARN_PCT

    if prev.get("swap_warned_prev", False) and swap_used <= SWAP_WARN_MB:
        alerts.append(("OK", "Swap kembali normal", f"{swap_used}MB/{swap_total}MB", ""))
    prev["swap_warned_prev"] = swap_used > SWAP_WARN_MB

    save_state(prev)

    if not alerts:
        log.persist()
        return

    level = "CRITICAL" if any(a[0] == "CRITICAL" for a in alerts) else "WARNING"
    msg = TelegramMessage("📈 MemStat", "", level=level)
    for lvl, title, detail, rec in alerts:
        msg.add_alert(lvl, title, detail, rec)

    msg.add_table(
        ["Komponen", "Pemakaian", "Bar"],
        [
            ["RAM", f"{mem_pct}% ({mem_used}MB/{mem_total}MB)", progress_bar(mem_pct)],
            ["Swap", f"{swap_pct}% ({swap_used}MB/{swap_total}MB)", progress_bar(swap_pct)],
        ],
    )

    print(msg.render())
    log.persist()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("MemStat error", "Coba jalankan ulang")
        report = log.format_report()
        if report:
            print(report)
        log.persist()
