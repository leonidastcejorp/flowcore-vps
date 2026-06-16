#!/usr/bin/env python3
"""📡 SysWatch — ngasih tau kalo VPS bermasalah (RAM, disk, CPU)."""
import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from error_log import ErrorLog

log = ErrorLog("📡 SysWatch")
WIB = datetime.now().strftime("%Y-%m-%d %H:%M WIB")


def run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.returncode == 0
    except subprocess.TimeoutExpired:
        log.warning("Perintah lambat", f"`{cmd[:50]}...` gak selesai", "Coba ulang manual")
        return "", False
    except FileNotFoundError:
        log.error("Perintah gak ditemukan", f"`{cmd.split()[0]}` gak ada", "Cek PATH / install")
        return "", False
    except OSError as e:
        log.error("Gagal jalanin perintah", f"Error: {e}", "Cek permissions / disk")
        return "", False


def bar(pct, w=8):
    f = round(min(pct, 100) / 100 * w)
    return "█" * f + "░" * (w - f)


def check():
    lines = []
    alerts = []
    recs = []

    # ── RAM ──
    out, ok = run("free | grep Mem | awk '{printf \"%.0f\", $3/$2 * 100}'")
    ram_data = {}
    if not ok or not out or not out.isdigit():
        log.error("Gagal baca RAM", "Perintah `free` error", "Cek `free -h` manual")
    else:
        ram_pct = int(out)
        full, _ = run("free -h | grep Mem:")
        parts = full.split()
        ram_data = {"used": parts[2] if len(parts) > 2 else "?", "total": parts[1] if len(parts) > 1 else "?"}

        if ram_pct >= 92:
            sisa = ((100 - ram_pct) / 100 * 2)
            alerts.append(f"RAM")
            alerts.append(f"• Pemakaian: {ram_pct}% ({ram_data['used']}/{ram_data['total']}) — KRITIS!")
            alerts.append(f"• Dampak: Sisa cuma {sisa:.1f}GB — OOM kapan aja")
            alerts.append(f"• Saran: Matikan program berat sekarang!")
            log.critical("RAM mau habis", f"{ram_pct}% — sisa {sisa:.1f}GB", "Matikan program berat!")
        elif ram_pct >= 82:
            alerts.append(f"RAM")
            alerts.append(f"• Pemakaian: {ram_pct}% ({ram_data['used']}/{ram_data['total']})")
            alerts.append(f"• Dampak: Sistem mulai lemot")
            alerts.append(f"• Saran: `sync && echo 3 > /proc/sys/vm/drop_caches`")
            log.warning("RAM tinggi", f"{ram_pct}%", "Bersihin cache: sync && echo 3...")
        elif ram_pct >= 70:
            alerts.append(f"RAM")
            alerts.append(f"• Pemakaian: {ram_pct}% ({ram_data['used']}/{ram_data['total']})")
            alerts.append(f"• Saran: Pantau, restart Hermes kalo naik 5% lagi")
            log.info("RAM waspada", f"{ram_pct}%")

    # ── DISK ──
    out, ok = run("df -h / | tail -1")
    disk_data = {}
    if not ok or not out:
        log.error("Gagal baca disk", "`df -h` error", "Cek manual")
    else:
        parts = out.split()
        disk_data = {"used": parts[2] if len(parts) > 2 else "?", "total": parts[1] if len(parts) > 1 else "?"}
        pct_str = parts[4] if len(parts) > 4 else "0%"
        try:
            disk_pct = int(pct_str.rstrip("%"))
        except (ValueError, IndexError):
            disk_pct = 0

        if disk_pct >= 93:
            sisa = ((100 - disk_pct) / 100 * 40)
            alerts.append(f"Disk")
            alerts.append(f"• Pemakaian: {disk_pct}% ({disk_data['used']}/{disk_data['total']}) — KRITIS!")
            alerts.append(f"• Dampak: Sisa cuma {sisa:.1f}GB")
            alerts.append(f"• Saran: `journalctl --vacuum-size=500M`")
            log.critical("Disk mau penuh", f"{disk_pct}% — sisa {sisa:.1f}GB", "Hapus log: journalctl...")
        elif disk_pct >= 88:
            alerts.append(f"Disk")
            alerts.append(f"• Pemakaian: {disk_pct}% ({disk_data['used']}/{disk_data['total']})")
            alerts.append(f"• Saran: `apt clean` & hapus file log")
            log.warning("Disk hampir penuh", f"{disk_pct}%", "apt clean")
        elif disk_pct >= 78:
            alerts.append(f"Disk")
            alerts.append(f"• Pemakaian: {disk_pct}% ({disk_data['used']}/{disk_data['total']})")
            minggu = int((100 - disk_pct) / 5)
            alerts.append(f"• Saran: Sisa ~{minggu} minggu — pantau")
            log.info("Disk mulai penuh", f"{disk_pct}% — ~{minggu} minggu lagi")

    # ── CPU ──
    load_out, _ = run("uptime | grep -oP 'load average:.*' | cut -d: -f2")
    cores_str, _ = run("nproc")
    cores = int(cores_str) if cores_str and cores_str.isdigit() else 2
    vals = [float(x) for x in load_out.replace(",", "").split() if x.replace(".", "").isdigit()]
    cpu_data = {}
    if not vals:
        log.error("Gagal baca CPU", "Output uptime error", "Cek `uptime`")
    else:
        load = vals[0]
        util = (load / cores) * 100
        cpu_data["load"] = f"{load:.1f}/{cores}core"
        if util >= 150:
            alerts.append(f"CPU")
            alerts.append(f"• Beban: {load:.1f}/{cores}core — OVERLOAD!")
            alerts.append(f"• Dampak: VPS lemot banget")
            alerts.append(f"• Saran: Cek `htop`, matikan yg gak penting")
            log.critical("CPU overload", f"Load {load:.1f}/{cores}c", "Cek htop")
        elif util >= 100:
            alerts.append(f"CPU")
            alerts.append(f"• Beban: {load:.1f}/{cores}core — penuh")
            alerts.append(f"• Saran: `ps aux --sort=-%cpu | head -5`")
            log.warning("CPU penuh", f"Load {load:.1f}/{cores}c", "Cek proses")
        elif util >= 70:
            log.info("CPU tinggi", f"Load {load:.1f}/{cores}c")

    # ── Output ──
    header_icon = "💀" if any(e["level"] == "CRITICAL" for e in log.entries) else \
                  "🔴" if any(e["level"] == "ERROR" for e in log.entries) else \
                  "🟡" if any(e["level"] == "WARNING" for e in log.entries) else "✅"

    if not alerts:
        lines.append(f"{header_icon} 📡 SysWatch")
        lines.append("")
        if ram_data:
            lines.append("RAM")
            lines.append(f"• Pemakaian: {ram_pct}% ({ram_data['used']}/{ram_data['total']})")
            lines.append("")
        if disk_data:
            lines.append("Disk")
            lines.append(f"• Pemakaian: {disk_pct}% ({disk_data['used']}/{disk_data['total']})")
            lines.append("")
        if cpu_data:
            lines.append("CPU")
            lines.append(f"• Beban: {cpu_data['load']}")
            lines.append("")
        lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
        log.persist()
        print("\n".join(lines))
        return

    # Ada masalah
    lines.append(f"{header_icon} 📡 SysWatch")
    lines.append("")
    for a in alerts:
        lines.append(a)
    lines.append("")
    if recs:
        for r in recs:
            lines.append(r)
        lines.append("")

    err_report = log.format_report()
    if err_report:
        lines.append(err_report)
        lines.append("")

    lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
    log.persist()
    print("\n".join(lines))


if __name__ == "__main__":
    try:
        check()
    except Exception:
        log.exception("Watchdog error", "Coba jalankan ulang")
        print(f"🔴 📡 SysWatch\n\n🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
