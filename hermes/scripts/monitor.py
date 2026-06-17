#!/usr/bin/env python3
"""
📡 VitalSign — alert monitor RAM/disk/CPU. Aman = silent.
"""
import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from error_log import ErrorLog
from telegram_ui import TelegramMessage, progress_bar

log = ErrorLog("📡 VitalSign")


def run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.returncode == 0
    except subprocess.TimeoutExpired:
        log.error("Timeout", f"`{cmd}` lewat {timeout}s", "Cek load VPS")
        return "", False
    except FileNotFoundError:
        log.error("Perintah gak ada", f"`{cmd.split()[0]}` tidak ditemukan", "Cek PATH")
        return "", False


def check():
    alerts = []
    table_rows = []
    has_issue = False

    # RAM
    out, ok = run("free | grep Mem | awk '{printf \"%.0f\", $3/$2 * 100}'")
    ram_pct = int(out) if ok and out.isdigit() else None
    if ram_pct is not None:
        full, _ = run("free -h | grep Mem:")
        parts = full.split()
        used = parts[2] if len(parts) > 2 else "?"
        total = parts[1] if len(parts) > 1 else "?"
        if ram_pct >= 92:
            alerts.append(("CRITICAL", "RAM kritis", f"{ram_pct}% ({used}/{total})", "Matikan program berat segera"))
            log.critical("RAM kritis", f"{ram_pct}%", "Matikan program berat")
            has_issue = True
        elif ram_pct >= 82:
            alerts.append(("WARNING", "RAM tinggi", f"{ram_pct}% ({used}/{total})", "Bersihin cache atau restart service"))
            log.warning("RAM tinggi", f"{ram_pct}%", "Bersihin cache")
            has_issue = True
        else:
            table_rows.append(["RAM", f"{ram_pct}%", progress_bar(ram_pct)])
    else:
        log.error("Gagal baca RAM", "Perintah free error", "Cek manual")

    # Disk
    out, ok = run("df -h / | tail -1")
    if ok and out:
        parts = out.split()
        used = parts[2] if len(parts) > 2 else "?"
        total = parts[1] if len(parts) > 1 else "?"
        try:
            disk_pct = int(parts[4].rstrip("%"))
        except (ValueError, IndexError):
            disk_pct = 0
        if disk_pct >= 93:
            alerts.append(("CRITICAL", "Disk kritis", f"{disk_pct}% ({used}/{total})", "Hapus log & cache segera"))
            log.critical("Disk kritis", f"{disk_pct}%", "Hapus log & cache")
            has_issue = True
        elif disk_pct >= 88:
            alerts.append(("WARNING", "Disk tinggi", f"{disk_pct}% ({used}/{total})", "Bersihin apt cache & log"))
            log.warning("Disk tinggi", f"{disk_pct}%", "Bersihin apt cache & log")
            has_issue = True
        else:
            table_rows.append(["Disk", f"{disk_pct}%", progress_bar(disk_pct)])
    else:
        log.error("Gagal baca disk", "Perintah df error", "Cek manual")

    # CPU
    load_out, _ = run("uptime | grep -oP 'load average:.*' | cut -d: -f2")
    cores_str, _ = run("nproc")
    cores = int(cores_str) if cores_str and cores_str.isdigit() else 2
    vals = [float(x) for x in load_out.replace(",", "").split() if x.replace(".", "").isdigit()]
    if vals:
        load = vals[0]
        util = (load / cores) * 100
        if util >= 150:
            alerts.append(("CRITICAL", "CPU overload", f"load {load:.1f}/{cores}c", "Matikan proses berat"))
            log.critical("CPU overload", f"{load:.1f}/{cores}c", "Matikan proses berat")
            has_issue = True
        elif util >= 100:
            alerts.append(("ERROR", "CPU penuh", f"load {load:.1f}/{cores}c", "Cek htop & kill proses"))
            log.error("CPU penuh", f"{load:.1f}/{cores}c", "Cek htop")
            has_issue = True
        elif util >= 70:
            alerts.append(("WARNING", "CPU tinggi", f"load {load:.1f}/{cores}c", "Tunda spawn task baru"))
            log.warning("CPU tinggi", f"{load:.1f}/{cores}c", "Tunda task baru")
            has_issue = True
        else:
            table_rows.append(["CPU", f"{load:.1f}/{cores}c", progress_bar(util)])

    if not has_issue:
        log.persist()
        return

    level = "CRITICAL" if any(a[0] == "CRITICAL" for a in alerts) else "ERROR" if any(a[0] == "ERROR" for a in alerts) else "WARNING"
    msg = TelegramMessage("📡 VitalSign", "", level=level)
    for lvl, title, detail, rec in alerts:
        msg.add_alert(lvl, title, detail, rec)

    if table_rows:
        msg.add_text("**Komponen lain:**")
        msg.add_table(["Komponen", "Pemakaian", "Bar"], table_rows)

    print(msg.render())
    log.persist()


if __name__ == "__main__":
    try:
        check()
    except Exception:
        log.exception("VitalSign error", "Coba jalankan ulang")
        report = log.format_report()
        if report:
            print(report)
        log.persist()
