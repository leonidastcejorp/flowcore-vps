#!/usr/bin/env python3
"""📈 Memory Monitor — ngasih tau kalo RAM mau habis atau OOM."""
import json
import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from error_log import ErrorLog

STATE_FILE = os.path.expanduser("~/.hermes/scripts/.memory_state.json")
SWAP_WARN_MB = 500
MEM_WARN_PCT = 90

log = ErrorLog("📈 MemStat")


def cek(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.returncode == 0
    except:
        return "", False


def tabel(data):
    """Markdown table buat Telegram."""
    rows = ["| Komponen | Pemakaian |", "|----------|-----------|"]
    for label, value in data:
        rows.append(f"| {label} | {value} |")
    return "\n".join(rows)


def main():
    output_parts = []
    table_data = []
    alerts = []

    # ── Baca RAM & Swap ──
    raw, ok = cek(["free", "-m"])
    if ok and raw:
        lines = raw.split("\n")
        try:
            mem = [c for c in lines if c.startswith("Mem:")][0].split()
            swap = [c for c in lines if c.startswith("Swap:")][0].split()

            mem_total = int(mem[1])
            mem_used = int(mem[2])
            mem_avail = int(mem[6])
            mem_pct = int(mem_used * 100 / mem_total)

            swap_total = int(swap[1])
            swap_used = int(swap[2])
            swap_pct = int(swap_used * 100 / swap_total) if swap_total > 0 else 0

            table_data.append(("RAM", f"{mem_pct}% ({mem_used}MB/{mem_total}MB)"))
            table_data.append(("Swap", f"{swap_pct}% ({swap_used}MB/{swap_total}MB)"))
        except (IndexError, ValueError, ZeroDivisionError, KeyError):
            log.error("Gagal baca memory", "Format `free -m` berubah.", "Cek `free -h` manual")
    else:
        log.error("Gagal baca memory", "Perintah `free -m` error.", "Coba `free -h` manual")

    # ── Cek OOM ──
    oom_raw, oom_ok = cek(["dmesg", "--level=emerg,alert,crit,err"])
    oom_count = 0
    if oom_ok:
        for line in (oom_raw or "").split("\n"):
            if "oom" in line.lower() or "out of memory" in line.lower():
                oom_count += 1
    elif oom_raw == "":
        pass
    else:
        log.warning("Gagal baca log kernel", "Akses terbatas — deteksi OOM mati", "Kasih akses? 1 perintah aja")

    # ── State ──
    prev = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                prev = json.load(f)
        except:
            prev = {}

    # ── Swap tinggi ──
    if swap_used and swap_used > SWAP_WARN_MB:
        if not prev.get("swap_warned", False):
            alerts.append(f"📈 **Swap mulai penuh** — {swap_used}MB/{swap_total}MB ({swap_pct}%)")
            alerts.append(f"RAM {mem_pct}% ({mem_avail}MB sisa)")
            alerts.append(f"→ Tutup aplikasi boros atau upgrade RAM")
            log.warning("Swap mulai tinggi", f"RAM abis buat swap {swap_used}MB", "Tutup aplikasi berat")
        prev["swap_warned"] = True
    else:
        prev["swap_warned"] = False

    # ── RAM kritis ──
    if mem_pct and mem_pct > MEM_WARN_PCT:
        if not prev.get("ram_critical_warned", False):
            alerts.append(f"🔴 **RAM mau habis!** {mem_pct}% ({mem_avail}MB sisa)")
            alerts.append(f"→ Segera tutup program atau matikan service")
            log.error("RAM kritis", f"{mem_pct}% — sisa {mem_avail}MB", "Tutup session atau matikan service")
        prev["ram_critical_warned"] = True
    else:
        prev["ram_critical_warned"] = False

    # ── OOM ──
    if oom_count > 0:
        prev_oom = prev.get("oom_count", 0)
        if oom_count > prev_oom:
            alerts.append(f"💥 **OOM Killer!** Sistem matiin program karena RAM abis ({oom_count}x)")
            alerts.append(f"→ Cek: `dmesg | grep -i oom`")
            log.critical("OOM — RAM abis", f"Sistem bunuh program {oom_count}x", "Free memory! Matikan program besar")
        prev["oom_count"] = oom_count

    # ── Recovery ──
    if prev.get("swap_warned_prev", False) and swap_used and swap_used <= SWAP_WARN_MB:
        alerts.append(f"✅ **Swap udah normal** — turun ke {swap_used}MB")
    prev["swap_warned_prev"] = swap_used > SWAP_WARN_MB if swap_used else False

    if prev.get("ram_critical_prev", False) and mem_pct and mem_pct <= MEM_WARN_PCT:
        alerts.append(f"✅ **RAM udah normal** — {mem_pct}% ({mem_avail}MB sisa)")
    prev["ram_critical_prev"] = mem_pct > MEM_WARN_PCT if mem_pct else False

    # ── Simpan state ──
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(prev, f)
    except OSError:
        log.error("Gagal simpan data", "File state gak bisa ditulis", "Cek disk")

    # ── OUTPUT ──
    has_issues = bool(alerts) or log.ada_masalah()

    # Header
    if has_issues:
        ico = "💀" if any(e["level"] == "CRITICAL" for e in log.entries) else \
              "🔴" if any(e["level"] == "ERROR" for e in log.entries) else "🟡"
        output_parts.append(f"{ico} **📈 MemStat**\n")
        output_parts.extend(alerts)
        output_parts.append("")
    else:
        output_parts.append(f"✅ **📈 MemStat**\n")

    # Status table
    if table_data:
        output_parts.append(tabel(table_data))
        output_parts.append("")

    # Error report from lib
    err_report = log.format_report()
    if err_report:
        output_parts.append(err_report)
        output_parts.append("")

    # Footer
    output_parts.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")

    print("\n".join(output_parts))
    log.persist()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("Error gak terduga", "Coba jalankan ulang")
        log.persist()
        report = log.format_report()
        if report:
            print(report)
