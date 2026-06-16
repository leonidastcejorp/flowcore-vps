#!/usr/bin/env python3
"""🚪 SSH Attack Monitor — ngasih tau kalo ada yang coba hack SSH."""
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

log = ErrorLog("🚪 PortGuard")


def tabel(data):
    rows = ["| Komponen | Status |", "|----------|--------|"]
    for label, value in data:
        rows.append(f"| {label} | {value} |")
    return "\n".join(rows)


def main():
    output_parts = []
    now = datetime.now()

    # ── Cek file fail2ban ──
    if not os.path.exists(F2B_LOG):
        log.warning("Log fail2ban ilang", "File log gak ditemukan — mungkin service mati", "Cek: fail2ban-client status")
        error_out()
        return

    try:
        result = subprocess.run(
            ["grep", "NOTICE.*Ban", F2B_LOG],
            capture_output=True, text=True, timeout=10
        )
    except subprocess.TimeoutExpired:
        log.error("Log gagal dibaca", "File terlalu besar — timeout", "Cek ukuran: ls -lh /var/log/fail2ban.log")
        error_out()
        return
    except FileNotFoundError:
        log.error("Perintah grep gak ada", "Sistem rusak!", "Install ulang coreutils")
        error_out()
        return

    raw = result.stdout.strip()
    if not raw:
        # Aman — gak ada ban
        output_parts.append(f"✅ **🚪 PortGuard**\n")
        output_parts.append(tabel([("Status", "Aman ✅"), ("Percobaan 24j", "0")]))
        output_parts.append("")
        output_parts.append(f"🕐 {now.strftime('%a %d %b %H:%M')}")
        print("\n".join(output_parts))
        return

    # ── Parse ──
    lines = raw.split("\n")
    bans = []
    for line in lines:
        if not line.strip():
            continue
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        ts = parts[0] + " " + parts[1].rstrip(",")
        ip = parts[-1]
        bans.append((ts, ip))

    # Filter 24 jam
    cutoff = now - timedelta(hours=24)
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")
    recent = [(ts, ip) for ts, ip in bans if ts >= cutoff_str]

    if not recent:
        output_parts.append(f"✅ **🚪 PortGuard**\n")
        output_parts.append(tabel([("Status", "Aman ✅"), ("Percobaan 24j", "0")]))
        output_parts.append("")
        output_parts.append(f"🕐 {now.strftime('%a %d %b %H:%M')}")
        print("\n".join(output_parts))
        return

    # ── State ──
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

    # Simpan state
    state = {
        "known_ips": list(current_ips),
        "last_notified_level": last_notified,
        "last_checked": now.isoformat(),
    }
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    except OSError:
        log.error("Gagal simpan data", "File state gak bisa ditulis", "Cek disk")

    # First run
    if last_notified == 999:
        return

    # ── Cek threshold ──
    if new_count <= AMBANG or new_count <= last_notified:
        # Aman — di bawah batas
        output_parts.append(f"✅ **🚪 PortGuard**\n")
        output_parts.append(tabel([
            ("Status", "Aman ✅"),
            ("Percobaan 24j", str(total_bans)),
            ("IP unik", str(len(current_ips))),
            ("IP baru", str(new_count)),
        ]))
        output_parts.append("")
        output_parts.append(f"🕐 {now.strftime('%a %d %b %H:%M')}")
        print("\n".join(output_parts))
        return

    # ── Update last_notified ──
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

    # ── Alert ──
    if new_count > 20:
        print(f"🔴 **SSH Diserang!** {new_count} IP baru nyoba login dalam 24 jam")
        log.critical("SSH diserang", f"{new_count} IP baru dari {total_unique}", "Ganti port atau pasang Cloudflare?")
    else:
        print(f"🟡 **Ada yang coba-coba SSH** — {new_count} IP baru")
        log.warning("Percobaan SSH", f"{new_count} IP baru", "Aman — fail2ban udah blokir")

    print(f"Total: {total_bans} percobaan dari {total_unique} IP berbeda")
    if top_ips:
        ips = "`" + "` `".join(top_ips) + "`"
        print(f"IP baru: {ips}{'...' if new_count > 5 else ''}")
    if new_count > 20:
        print("")
        print("⚠️ Saranku: ganti port SSH atau pasang Cloudflare WAF biar lebih aman")

    err_report = log.format_report()
    if err_report:
        print(f"\n{err_report}")

    log.persist()


def error_out():
    err_report = log.format_report()
    if err_report:
        print(err_report)
    log.persist()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("Error gak terduga", "Coba jalankan ulang")
        error_out()
