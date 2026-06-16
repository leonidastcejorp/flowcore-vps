#!/usr/bin/env python3
"""🔁 Reboot Monitor — ngasih tau kalo VPS tiba-tiba restart."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from error_log import ErrorLog

STATE_FILE = os.path.expanduser("~/.hermes/scripts/.boot_state.json")
log = ErrorLog("🔁 Bootmark")


def tabel(data):
    rows = ["| Komponen | Status |", "|----------|--------|"]
    for label, value in data:
        rows.append(f"| {label} | {value} |")
    return "\n".join(rows)


def main():
    output = []

    # ── Baca waktu boot ──
    try:
        result = subprocess.run(["uptime", "-s"], capture_output=True, text=True, timeout=5)
    except FileNotFoundError:
        log.error("Perintah uptime gak ada", "Program `uptime` gak ditemukan", "Reinstall procps")
        return finalize()
    except subprocess.TimeoutExpired:
        log.error("Perintah uptime lambat", "`uptime -s` timeout", "Cek sistem")
        return finalize()

    boot_sekarang = result.stdout.strip()
    if not boot_sekarang:
        log.error("Gagal baca waktu boot", "`uptime -s` kosong", "Cek manual")
        return finalize()

    try:
        boot_dt = datetime.strptime(boot_sekarang, "%Y-%m-%d %H:%M:%S")
        boot_ts = boot_dt.replace(tzinfo=timezone.utc).timestamp()
    except ValueError:
        log.error("Format waktu boot aneh", f"Output: '{boot_sekarang}'", "Cek `uptime -s`")
        return finalize()

    # ── Baca boot sebelumnya ──
    boot_sebelumnya = None
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                d = json.load(f)
                boot_sebelumnya = d.get("boot_time")
        except:
            pass

    # ── Simpan boot sekarang ──
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump({
                "boot_time": boot_sekarang,
                "boot_ts": boot_ts,
                "last_checked": datetime.now().isoformat()
            }, f)
    except OSError:
        log.error("Gagal simpan data boot", "File state gak bisa ditulis", "Cek disk")

    # First run
    if boot_sebelumnya is None:
        return finalize()

    # ── Cek restart ──
    if boot_sekarang == boot_sebelumnya:
        # Stabil — tabel status
        uptime_raw = subprocess.run(["uptime", "-p"], capture_output=True, text=True).stdout.strip()
        uptime_str = uptime_raw.replace("up ", "")
        output.append(f"✅ **🔁 Bootmark**\n")
        output.append(tabel([("Boot", boot_sekarang), ("Uptime", uptime_str)]))
        output.append("")
        output.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
        print("\n".join(output))
        return

    # RESTART!
    try:
        prev_dt = datetime.strptime(boot_sebelumnya, "%Y-%m-%d %H:%M:%S")
        prev_dt = prev_dt.replace(tzinfo=timezone.utc)
        downtime = boot_ts - prev_dt.timestamp()
    except:
        downtime = -1

    if downtime < 60:
        durasi = "<1 menit"
    elif downtime < 300:
        durasi = f"~{int(downtime)} detik"
    else:
        durasi = f"~{int(downtime/60)} menit"

    print(f"🔁 **VPS Restart!** Down {durasi}")
    print(f"   Boot sebelumnya: {boot_sebelumnya}")
    print(f"   Boot sekarang:   {boot_sekarang}")
    print(f"   → Cek penyebab: `journalctl -xb -n 50`")

    log.critical("VPS restart", f"Down {durasi}", "Cek: journalctl -xb -n 50")

    err_report = log.format_report()
    if err_report:
        print(f"\n{err_report}")

    log.persist()


def finalize():
    report = log.format_report()
    if report:
        print(report)
    log.persist()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("Error gak terduga", "Coba jalankan ulang")
        finalize()
