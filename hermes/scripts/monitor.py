#!/usr/bin/env python3
"""📡 Server Watchdog — ngasih tau kalo VPS bermasalah (RAM, disk, CPU)."""
import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from error_log import ErrorLog

log = ErrorLog("📡 VitalSign")
WIB = datetime.now().strftime("%Y-%m-%d %H:%M WIB")


def run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip(), r.returncode == 0
    except subprocess.TimeoutExpired:
        return "", False
    except FileNotFoundError:
        log.error("Perintah gak ditemukan", f"Program `{cmd.split()[0]}` gak ada", "Cek PATH / install ulang")
        return "", False
    except OSError as e:
        log.error("Gagal jalanin perintah", f"Error: {e}", "Cek permissions / disk")
        return "", False


def bar(pct, w=8):
    f = round(min(pct, 100) / 100 * w)
    return "█" * f + "░" * (w - f)


def tabel(data):
    rows = ["| Komponen | Status |", "|----------|--------|"]
    for label, value in data:
        rows.append(f"| {label} | {value} |")
    return "\n".join(rows)


def check():
    alerts = []
    recs = []
    table_data = []
    has_issue = False

    # ── RAM ──
    out, ok = run("free | grep Mem | awk '{printf \"%.0f\", $3/$2 * 100}'")
    if ok and out and out.isdigit():
        ram_pct = int(out)
        full, _ = run("free -h | grep Mem:")
        parts = full.split()
        used = parts[2] if len(parts) > 2 else "?"
        total = parts[1] if len(parts) > 1 else "?"

        if ram_pct >= 92:
            sisa = ((100 - ram_pct) / 100 * 2)
            alerts.append(f"💀 **RAM kritis!** {ram_pct}% ({used}/{total}) — sisa {sisa:.1f}GB")
            alerts.append(f"`     `{bar(ram_pct)}")
            recs.append(f"💾 Segera matikan program berat!")
            log.critical("RAM mau habis", f"{ram_pct}% — sisa {sisa:.1f}GB", "Matikan program berat")
            has_issue = True
        elif ram_pct >= 82:
            alerts.append(f"🔴 **RAM bahaya** {ram_pct}% ({used}/{total})")
            alerts.append(f"`     `{bar(ram_pct)}")
            recs.append(f"💾 Bersihin cache: `sync && echo 3 > /proc/sys/vm/drop_caches`")
            has_issue = True
        elif ram_pct >= 70:
            alerts.append(f"🟡 **RAM waspada** {ram_pct}% ({used}/{total})")
            alerts.append(f"`     `{bar(ram_pct)}")
            recs.append(f"💾 Pantau, restart Hermes kalo naik lagi")
            has_issue = True
        else:
            table_data.append(("RAM", f"{ram_pct}% ({used}/{total})"))
    else:
        log.error("Gagal baca RAM", "Perintah `free` error", "Cek `free -h` manual")

    # ── DISK ──
    out, ok = run("df -h / | tail -1")
    if ok and out:
        parts = out.split()
        used = parts[2] if len(parts) > 2 else "?"
        total = parts[1] if len(parts) > 1 else "?"
        pct_str = parts[4] if len(parts) > 4 else "0%"
        try:
            disk_pct = int(pct_str.rstrip("%"))
        except (ValueError, IndexError):
            log.error("Gagal baca angka disk", f"Output: {pct_str}", "Cek `df -h`")
            disk_pct = 0

        if disk_pct >= 93:
            sisa = ((100 - disk_pct) / 100 * 40)
            alerts.append(f"💀 **Disk kritis!** {disk_pct}% ({used}/{total}) — sisa {sisa:.1f}GB")
            alerts.append(f"`     `{bar(disk_pct)}")
            recs.append(f"💽 Hapus log: `journalctl --vacuum-size=500M`")
            log.critical("Disk mau penuh", f"{disk_pct}% — sisa {sisa:.1f}GB", "journalctl --vacuum-size=500M")
            has_issue = True
        elif disk_pct >= 88:
            alerts.append(f"🔴 **Disk bahaya** {disk_pct}% ({used}/{total})")
            alerts.append(f"`     `{bar(disk_pct)}")
            recs.append(f"💽 Bersihin: `apt clean` & hapus file log lama")
            has_issue = True
        elif disk_pct >= 78:
            alerts.append(f"🟡 **Disk waspada** {disk_pct}% ({used}/{total})")
            alerts.append(f"`     `{bar(disk_pct)}")
            recs.append(f"💽 ~{int((100-disk_pct)/5)} minggu lagi perlu cleanup")
            has_issue = True
        else:
            table_data.append(("Disk", f"{disk_pct}% ({used}/{total})"))
    else:
        log.error("Gagal baca disk", "Perintah `df -h` error", "Cek `df -h` manual")

    # ── CPU ──
    load_out, _ = run("uptime | grep -oP 'load average:.*' | cut -d: -f2")
    cores_str, _ = run("nproc")
    cores = int(cores_str) if cores_str and cores_str.isdigit() else 2
    vals = [float(x) for x in load_out.replace(",", "").split() if x.replace(".", "").isdigit()]

    if vals:
        load = vals[0]
        util = (load / cores) * 100
        if util >= 150:
            alerts.append(f"💀 **CPU overload!** {load:.1f}/2c ({util:.0f}%)")
            recs.append(f"🧠 Cek `htop`, matikan program gak penting")
            log.critical("CPU overload", f"{load:.1f}/2c ({util:.0f}%)", "Cek htop & matikan yg boros")
            has_issue = True
        elif util >= 100:
            alerts.append(f"🔴 **CPU penuh!** {load:.1f}/2c")
            recs.append(f"🧠 Cek: `ps aux --sort=-%cpu | head -5`")
            has_issue = True
        elif util >= 70:
            alerts.append(f"🟡 **CPU tinggi** {load:.1f}/2c ({util:.0f}%)")
            recs.append(f"🧠 Jangan spawn task baru dulu")
            has_issue = True
        else:
            table_data.append(("CPU", f"{load:.1f}/2c"))
    else:
        log.error("Gagal baca CPU", "Output `uptime` error", "Cek `uptime` manual")

    # ── OUTPUT ──
    output = []

    if has_issue:
        # Ada masalah — format alert dulu
        output.append(f"🚨 **📡 VitalSign**")
        output.append(f"`{WIB}`\n")
        for a in alerts:
            output.append(a)
        if recs:
            output.append("")
            output.append("**💡 Saranku:**")
            for r in recs:
                output.append(r)
        if table_data:
            output.append("")
            output.append(tabel(table_data))
        output.append("")
        output.append("━━━━━━━━━━━━━━━━━━━")
    else:
        # Sehat — langsung tabel
        if table_data:
            output.append(f"✅ **📡 VitalSign**\n")
            output.append(tabel(table_data))
            output.append("")
            output.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")

    # Error report dari lib
    err_report = log.format_report()
    if err_report and has_issue:
        output.append("")
        output.append(err_report)

    if output:
        print("\n".join(output))

    log.persist()


if __name__ == "__main__":
    try:
        check()
    except Exception:
        log.exception("Watchdog error", "Coba jalankan ulang")
        report = log.format_report()
        if report:
            print(report)
        log.persist()
