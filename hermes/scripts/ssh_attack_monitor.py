#!/usr/bin/env python3
"""🚪 SSHDWatch — ngasih tau kalo ada yang coba-coba hack SSH."""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from error_log import ErrorLog

STATE_FILE = os.path.expanduser("~/.hermes/scripts/.ssh_attack_state.json")
AMBANG = 5
F2B_LOG = "/var/log/fail2ban.log"
log = ErrorLog("🚪 SSHDWatch")


def main():
    lines = []

    if not os.path.exists(F2B_LOG):
        log.warning("Gak nemuin log fail2ban", "File catatan fail2ban gak ada", "Cek: `fail2ban-client status`")
        return finalize(lines)

    try:
        result = subprocess.run(["grep", "NOTICE.*Ban", F2B_LOG], capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        log.error("Log fail2ban kebesaran", "Baca file terlalu lama", "Cek ukuran file")
        return finalize(lines)
    except FileNotFoundError:
        log.error("Perintah grep gak ada", "Program grep gak ditemukan", "Install coreutils")
        return finalize(lines)

    raw = result.stdout.strip()
    if not raw:
        lines.append(f"✅ 🚪 SSHDWatch")
        lines.append("")
        lines.append("Status")
        lines.append("• Aman — gak ada yang nyoba hack")
        lines.append("")
        lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
        log.persist()
        print("\n".join(lines))
        return

    bans = []
    gagal = 0
    for line in raw.split("\n"):
        if not line.strip():
            continue
        parts = line.strip().split()
        if len(parts) < 2:
            gagal += 1
            continue
        ts = parts[0] + " " + parts[1].rstrip(",")
        ip = parts[-1]
        bans.append((ts, ip))

    now = datetime.now()
    cutoff = now - timedelta(hours=24)
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")
    recent = [(ts, ip) for ts, ip in bans if ts >= cutoff_str]

    if not recent:
        lines.append(f"✅ 🚪 SSHDWatch")
        lines.append("")
        lines.append("Status")
        lines.append("• Aman — gak ada percobaan 24 jam terakhir")
        lines.append("")
        lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
        log.persist()
        print("\n".join(lines))
        return

    prev_ips = set()
    last_notified = 999
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                d = json.load(f)
                prev_ips = set(d.get("known_ips", []))
                last_notified = d.get("last_notified_level", 999)
        except:
            pass

    current_ips = set(ip for _, ip in recent)
    total_bans = len(recent)
    new_ips = current_ips - prev_ips
    new_count = len(new_ips)

    state = {"known_ips": list(current_ips), "last_notified_level": last_notified, "last_checked": now.isoformat()}
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    except OSError:
        log.error("Gagal simpan data", "File state gak bisa ditulis", "Cek disk")

    if last_notified == 999:
        lines.append(f"✅ 🚪 SSHDWatch")
        lines.append("")
        lines.append("Status")
        lines.append(f"• Pantauan dimulai — {total_bans} percobaan dari {len(current_ips)} IP")
        lines.append("")
        lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
        log.persist()
        print("\n".join(lines))
        return

    if new_count <= AMBANG or new_count <= last_notified:
        lines.append(f"✅ 🚪 SSHDWatch")
        lines.append("")
        lines.append("Status")
        lines.append(f"• Aman — cuma {new_count} IP baru (di bawah batas)")
        lines.append("")
        lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
        log.persist()
        print("\n".join(lines))
        return

    try:
        with open(STATE_FILE) as f:
            d = json.load(f)
        d["last_notified_level"] = new_count
        with open(STATE_FILE, 'w') as f:
            json.dump(d, f)
    except:
        pass

    total_unique = len(current_ips)
    top_ips = sorted(new_ips)[:5]

    if new_count > 20:
        icon = "🔴"
        label = "Serangan massal!"
        log.critical("Banyak IP nyoba hack SSH", f"{new_count} IP baru, {total_unique} unik", "Ganti port SSH / Cloudflare WAF")
    else:
        icon = "🟡"
        label = "Ada yang coba-coba"
        log.warning("Ada percobaan hack SSH", f"{new_count} IP baru", "Gak usah khawatir — fail2ban udah blokir")

    lines.append(f"{icon} 🚪 SSHDWatch")
    lines.append("")
    lines.append("Status")
    lines.append(f"• {label} — {new_count} IP baru (24 jam)")
    lines.append(f"• Total: {total_bans}x percobaan")
    lines.append(f"• IP beda: {total_unique} unik")
    if top_ips:
        ips = "`" + "` `".join(top_ips) + "`"
        lines.append(f"• IP baru: {ips}{'...' if new_count > 5 else ''}")
    lines.append("")

    if new_count > 20:
        lines.append("⚠️ Saran")
        lines.append("• Ganti port SSH atau pasang Cloudflare WAF")
        lines.append("")

    finalize(lines)


def finalize(lines=None):
    if lines is None:
        lines = []
    if not lines:
        lines.append(f"✅ 🚪 SSHDWatch")
        lines.append("")
        lines.append("Status")
        lines.append("• —")
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
        finalize()
