#!/usr/bin/env python3
"""🔁 Bootmark — ngasih tau kalo VPS tiba-tiba restart."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from error_log import ErrorLog

STATE_FILE = os.path.expanduser("~/.hermes/scripts/.boot_state.json")
log = ErrorLog("🔁 Bootmark")


def main():
    lines = []

    # ── Baca boot time ──
    try:
        result = subprocess.run(["uptime", "-s"], capture_output=True, text=True, timeout=5)
    except FileNotFoundError:
        log.error("Perintah uptime gak ada", "Program `uptime` gak ditemukan", "Reinstall procps")
        return finalize(lines)
    except subprocess.TimeoutExpired:
        log.error("Perintah uptime lambat", "`uptime -s` gak selesai", "Cek sistem")
        return finalize(lines)

    boot_sekarang = result.stdout.strip()
    if not boot_sekarang:
        log.error("Gagal baca boot", "`uptime -s` kosong", "Cek manual `uptime -s`")
        return finalize(lines)

    try:
        boot_dt = datetime.strptime(boot_sekarang, "%Y-%m-%d %H:%M:%S")
        boot_ts = boot_dt.replace(tzinfo=timezone.utc).timestamp()
    except ValueError:
        log.error("Format boot aneh", f"Output: '{boot_sekarang}'", "Cek `uptime -s`")
        return finalize(lines)

    # ── Hitung uptime ──
    sekarang_ts = datetime.now().timestamp()
    uptime_detik = int(sekarang_ts - boot_ts)

    if uptime_detik < 60:
        uptime_str = f"{uptime_detik} detik"
    elif uptime_detik < 3600:
        uptime_str = f"{uptime_detik // 60} menit"
    elif uptime_detik < 86400:
        jam = uptime_detik // 3600
        menit = (uptime_detik % 3600) // 60
        uptime_str = f"{jam} jam, {menit} menit"
    else:
        hari = uptime_detik // 86400
        jam = (uptime_detik % 86400) // 3600
        uptime_str = f"{hari} hari, {jam} jam"

    # ── Baca boot sebelumnya ──
    boot_sebelumnya = None
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                d = json.load(f)
                boot_sebelumnya = d.get("boot_time")
        except:
            pass

    # ── Simpan ──
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump({
                "boot_time": boot_sekarang,
                "boot_ts": boot_ts,
                "last_checked": datetime.now().isoformat()
            }, f)
    except OSError:
        log.error("Gagal simpan data", "File state gak bisa ditulis", "Cek disk")

    # ── Format output ──
    icon = "💀" if any(e["level"] == "CRITICAL" for e in log.entries) else \
           "🔴" if any(e["level"] == "ERROR" for e in log.entries) else \
           "🟡" if any(e["level"] == "WARNING" for e in log.entries) else "✅"

    lines.append(f"{icon} 🔁 Bootmark")
    lines.append("")
    lines.append("Boot")
    lines.append(f"• Status: {boot_sekarang}")
    lines.append("")
    lines.append("Uptime")
    lines.append(f"• Status: {uptime_str}")
    lines.append("")

    # ── Cek restart ──
    if boot_sebelumnya and boot_sekarang != boot_sebelumnya:
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

        lines.append("⚠️ **VPS Restart terdeteksi!**")
        lines.append(f"• Down: {durasi}")
        lines.append(f"• Sebelum: {boot_sebelumnya}")
        lines.append(f"• Saran: Cek `journalctl -xb -n 50`")
        lines.append("")

        log.critical("VPS restart", f"Down {durasi}. Sebelum: {boot_sebelumnya}", "Cek: journalctl -xb -n 50")

    err_report = log.format_report()
    if err_report:
        lines.append(err_report)
        lines.append("")

    lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")

    log.persist()
    print("\n".join(lines))


def finalize(lines):
    if not lines:
        boot_sekarang = subprocess.run(["uptime", "-s"], capture_output=True, text=True, timeout=5).stdout.strip() or "?"
        lines.append(f"✅ 🔁 Bootmark")
        lines.append("")
        lines.append("Boot")
        lines.append(f"• Status: {boot_sekarang}")
        lines.append("")
        lines.append("Uptime")
        lines.append("• Status: ?")
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
        main()
    except Exception:
        log.exception("Error gak terduga", "Coba jalankan ulang")
        from datetime import datetime
        boot = subprocess.run(["uptime", "-s"], capture_output=True, text=True, timeout=5).stdout.strip() or "?"
        print(f"✅ 🔁 Bootmark\n\nBoot\n• Status: {boot}\n\n🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
