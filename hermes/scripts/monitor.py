#!/usr/bin/env python3
"""
📡 FBI Watchdog — Server Emergency Monitor
Silent when all clear. Reports issues with recommendations.
Thresholds calculated based on 2c/2GB/40GB VPS specs.
"""
import os
import subprocess
from datetime import datetime

HOME = os.path.expanduser("~")
HERMES_DIR = os.path.join(HOME, ".hermes")
WIB = datetime.now().strftime("%Y-%m-%d %H:%M WIB")


def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return r.stdout.strip()
    except:
        return ""


def bar(pct, w=8):
    """Compact progress bar."""
    f = round(min(pct, 100) / 100 * w)
    return "█" * f + "░" * (w - f)


def ram_calc(pct, total_gb):
    """Return (emoji, zone_label, recommendation) based on RAM %."""
    if pct >= 92:
        return ("💀", "KRITIS", f"Segera matikan service ga penting. Sisa {((100-pct)/100*total_gb):.1f}GB — OOM dalam hitungan menit!")
    if pct >= 82:
        return ("🔴", "BAHAYA", f"Bersihin cache: `sync && echo 3 > /proc/sys/vm/drop_caches`. Sisa {((100-pct)/100*total_gb):.1f}GB.")
    if pct >= 70:
        return ("🟡", "WASPADA", f"Pantau terus. Kalo naik 5% lagi, restart Hermes dulu: `systemctl restart hermes`.")
    return ("🟢", "AMAN", None)


def disk_calc(pct, total_gb):
    """Return (emoji, zone_label, recommendation) based on DISK %."""
    if pct >= 93:
        return ("💀", "KRITIS", f"Disk nyaris penuh! Hapus log: `journalctl --vacuum-size=500M`. Sisa {((100-pct)/100*total_gb):.1f}GB.")
    if pct >= 88:
        return ("🔴", "BAHAYA", f"Bersihin apt cache: `apt clean` & log lama: `find /var/log -name '*.gz' -delete`. Sisa {((100-pct)/100*total_gb):.1f}GB.")
    if pct >= 78:
        return ("🟡", "WASPADA", f"Growth rate ~200MB/minggu. Sisa {((100-pct)/100*total_gb):.1f}GB — {((100-pct)/5):.0f} minggu lagi penuh.")
    return ("🟢", "AMAN", None)


def cpu_calc(load_1min, cores):
    """Return (emoji, zone_label, recommendation) based on CPU load."""
    util_pct = (load_1min / cores) * 100
    if util_pct >= 150:
        return ("💀", "KRITIS", f"CPU overload {load_1min:.1f}/2c ({util_pct:.0f}%)! Cek proses: `htop`, matikan yg ga penting.")
    if util_pct >= 100:
        return ("🔴", "BAHAYA", f"CPU full! Load {load_1min:.1f} = 2 core penuh. Cek: `ps aux --sort=-%cpu | head -5`.")
    if util_pct >= 70:
        return ("🟡", "WASPADA", f"CPU tinggi {load_1min:.1f}/2c ({util_pct:.0f}%). Pantau, jangan spawn task baru.")
    return ("🟢", "AMAN", None)


def check():
    alerts = []
    recs = []
    wib = WIB

    # ── RAM ──
    ram_pct_str = run("free | grep Mem | awk '{printf \"%.0f\", $3/$2 * 100}'")
    ram_pct = int(ram_pct_str) if ram_pct_str.isdigit() else 0
    ram_full = run("free -h | grep Mem:")
    rp = ram_full.split()
    ram_used = rp[2] if len(rp) > 2 else "?"
    ram_total = rp[1] if len(rp) > 1 else "?"
    ram_total_gb = float(ram_total.replace("Gi", "").replace("G", "").replace(",", ".")) if "G" in ram_total else 2.0

    ram_ico, ram_zone, ram_rec = ram_calc(ram_pct, ram_total_gb)
    if ram_zone != "AMAN":
        alerts.append(f"{ram_ico}{ram_zone} RAM {ram_pct}% ({ram_used}/{ram_total})")
        alerts.append(f"`     `{bar(ram_pct)}")
        if ram_rec:
            recs.append(f"💾 RAM: {ram_rec}")

    # ── DISK ──
    disk = run("df -h / | tail -1")
    dp = disk.split()
    disk_used = dp[2] if len(dp) > 2 else "?"
    disk_total = dp[1] if len(dp) > 1 else "?"
    disk_pct_str = dp[4] if len(dp) > 4 else "?"
    disk_pct_int = int(disk_pct_str.rstrip("%"))
    disk_total_gb = float(disk_total.replace("G", "")) if "G" in disk_total else 40

    dsk_ico, dsk_zone, dsk_rec = disk_calc(disk_pct_int, disk_total_gb)
    if dsk_zone != "AMAN":
        alerts.append(f"{dsk_ico}{dsk_zone} DISK {disk_pct_int}% ({disk_used}/{disk_total})")
        alerts.append(f"`     `{bar(disk_pct_int)}")
        if dsk_rec:
            recs.append(f"💽 DISK: {dsk_rec}")

    # ── CPU ──
    cpu_load = run("uptime | grep -oP 'load average:.*' | cut -d: -f2").strip()
    cpu_cores = int(run("nproc") or 2)
    load_vals = [float(x) for x in cpu_load.replace(",", "").split() if x.replace(".", "").isdigit()]
    load_1min = load_vals[0] if load_vals else 0

    cpu_ico, cpu_zone, cpu_rec = cpu_calc(load_1min, cpu_cores)
    if cpu_zone != "AMAN":
        alerts.append(f"{cpu_ico}{cpu_zone} CPU load {cpu_load} ({cpu_cores}c)")
        if cpu_rec:
            recs.append(f"🧠 CPU: {cpu_rec}")

    # ── Output ──
    if not alerts:
        return  # Silent — all good

    print(f"🚨 **SERVER WATCHDOG**")
    print(f"`{wib}`")
    print("")
    for a in alerts:
        print(a)
    if recs:
        print("")
        print("**💡 Rekomendasi:**")
        for r in recs:
            print(r)
    print("")
    print("━━━━━━━━━━━━━━━━━━━")


if __name__ == "__main__":
    check()
