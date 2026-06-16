#!/usr/bin/env python3
"""📈 MemStat — ngasih tau pemakaian RAM & Swap."""
import json
import os
import subprocess
import sys

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


def main():
    lines = []

    # ── Baca RAM & Swap ──
    raw, ok = cek(["free", "-m"])
    if not ok or not raw:
        log.error("Gagal baca memory", "Perintah `free -m` gak bisa jalan", "Coba `free -h` manual")
        return finalize(lines)

    try:
        parts = raw.split("\n")
        mem = [c for c in parts if c.startswith("Mem:")][0].split()
        swap = [c for c in parts if c.startswith("Swap:")][0].split()
    except (IndexError, ValueError):
        log.error("Gagal baca data memory", "Format output `free -m` berubah", "Coba `free -h` manual")
        return finalize(lines)

    try:
        mem_total = int(mem[1])
        mem_used = int(mem[2])
        mem_pct = int(mem_used * 100 / mem_total)
        swap_total = int(swap[1])
        swap_used = int(swap[2])
        swap_pct = int(swap_used * 100 / swap_total) if swap_total > 0 else 0
    except (IndexError, ValueError, ZeroDivisionError):
        log.error("Gagal hitung memory", "Angka dari `free -m` error", "Cek sistem")
        return finalize(lines)

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
        log.warning("Log kernel", "Akses ke catatan sistem dibatasi", "Biar gua kasih akses?")

    # ── State ──
    prev = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                prev = json.load(f)
        except:
            prev = {}

    alerts = []

    # ── Swap tinggi ──
    if swap_used > SWAP_WARN_MB:
        if not prev.get("swap_warned", False):
            alerts.append(f"Swap")
            alerts.append(f"• Pemakaian: {swap_used}MB/{swap_total}MB ({swap_pct}%) — tinggi")
            alerts.append(f"• Dampak: Sistem bisa lemot kalo RAM penuh")
            alerts.append(f"• Saran: Tutup program boros memory")
            log.warning("Swap tinggi", f"{swap_used}MB/{swap_total}MB", "Tutup program boros memory")
        prev["swap_warned"] = True
    else:
        prev["swap_warned"] = False

    # ── RAM kritis ──
    if mem_pct > MEM_WARN_PCT:
        if not prev.get("ram_critical_warned", False):
            alerts.append(f"RAM")
            alerts.append(f"• Pemakaian: {mem_pct}% ({mem_used}MB/{mem_total}MB)")
            alerts.append(f"• Dampak: Sisa memory tinggal {(mem_total-mem_used)}MB!")
            alerts.append(f"• Saran: Segera tutup program besar atau restart Hermes")
            log.error("RAM kritis", f"{mem_pct}% — sisa {mem_total-mem_used}MB", "Tutup program besar")
        prev["ram_critical_warned"] = True
    else:
        prev["ram_critical_warned"] = False

    # ── OOM ──
    if oom_count > 0:
        prev_oom = prev.get("oom_count", 0)
        if oom_count > prev_oom:
            alerts.append(f"💥 OOM Killer")
            alerts.append(f"• Kejadian: {oom_count}x")
            alerts.append(f"• Dampak: Sistem matiin program karena RAM abis")
            alerts.append(f"• Saran: Cek `dmesg | grep -i oom`")
            log.critical("OOM — RAM habis", f"{oom_count}x kejadian", "Free memory segera!")
        prev["oom_count"] = oom_count

    # ── Recovery ──
    if prev.get("swap_warned_prev", False) and swap_used <= SWAP_WARN_MB:
        alerts.append("✅ Swap pulih — normal lagi")
    prev["swap_warned_prev"] = swap_used > SWAP_WARN_MB

    if prev.get("ram_critical_prev", False) and mem_pct <= MEM_WARN_PCT:
        alerts.append("✅ RAM pulih — normal lagi")
    prev["ram_critical_prev"] = mem_pct > MEM_WARN_PCT

    # ── Simpan ──
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(prev, f)
    except OSError:
        log.error("Gagal simpan data", "File state gak bisa ditulis", "Cek disk")

    # ── Format output ──
    icon = "💀" if any(e["level"] == "CRITICAL" for e in log.entries) else \
           "🔴" if any(e["level"] == "ERROR" for e in log.entries) else \
           "🟡" if any(e["level"] == "WARNING" for e in log.entries) else "✅"

    lines.append(f"{icon} 📈 MemStat")
    lines.append("")

    if alerts:
        for a in alerts:
            lines.append(a)
        lines.append("")

    # Always show RAM & Swap status
    lines.append("RAM")
    lines.append(f"• Pemakaian: {mem_pct}% ({mem_used}MB/{mem_total}MB)")
    lines.append("")
    lines.append("Swap")
    lines.append(f"• Pemakaian: {swap_pct}% ({swap_used}MB/{swap_total}MB)")
    lines.append("")

    # Error report (if any)
    err_report = log.format_report()
    if err_report:
        lines.append(err_report)
        lines.append("")

    lines.append(f"🕐 {__import__('datetime').datetime.now().strftime('%a %d %b %H:%M')}")

    log.persist()
    print("\n".join(lines))


def finalize(lines):
    if not lines:
        lines.append(f"✅ 📈 MemStat")
        lines.append("")
        lines.append("RAM")
        lines.append("• Pemakaian: —")
        lines.append("")
        lines.append("Swap")
        lines.append("• Pemakaian: —")
        lines.append("")
    err_report = log.format_report()
    if err_report:
        lines.append(err_report)
        lines.append("")
    lines.append(f"🕐 {__import__('datetime').datetime.now().strftime('%a %d %b %H:%M')}")
    log.persist()
    print("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("Error gak terduga", "Coba jalankan ulang")
        finalize([])
