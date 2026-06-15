#!/usr/bin/env python3
"""
📊 FBI Daily Briefing — Token Usage, RTK Savings & Errors
Runs daily at 23:00 WIB via cron job.
"""

import json
import os
import sqlite3
import subprocess
from datetime import datetime, timezone

HOME = os.path.expanduser("~")
HERMES_DIR = os.path.join(HOME, ".hermes")
STATE_DB = os.path.join(HERMES_DIR, "state.db")
ERROR_LOG = os.path.join(HERMES_DIR, "logs", "errors.log")
WIB = datetime.now().strftime("%Y-%m-%d %H:%M WIB")


def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return r.stdout.strip()
    except:
        return ""


def get_tokens():
    if not os.path.exists(STATE_DB):
        return None
    try:
        conn = sqlite3.connect(STATE_DB)
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        cutoff = today_start - 86400  # 24h ago

        # Last 24h
        rows = conn.execute("""
            SELECT 
                COUNT(*),
                COALESCE(SUM(input_tokens), 0),
                COALESCE(SUM(output_tokens), 0),
                COALESCE(SUM(estimated_cost_usd), 0),
                COALESCE(SUM(message_count), 0)
            FROM sessions WHERE started_at > ?
        """, (cutoff,)).fetchone()

        # Today only
        today = conn.execute("""
            SELECT 
                COUNT(*),
                COALESCE(SUM(input_tokens), 0),
                COALESCE(SUM(output_tokens), 0),
                COALESCE(SUM(estimated_cost_usd), 0)
            FROM sessions WHERE started_at > ?
        """, (today_start,)).fetchone()

        conn.close()

        if rows[0] > 0:
            total_in = rows[1] + today[1]
            total_out = rows[2] + today[2]
            return {
                "sessions": rows[0],
                "messages": rows[4],
                "input": rows[1],
                "output": rows[2],
                "total": rows[1] + rows[2],
                "cost": rows[3],
                "today_sessions": today[0],
                "today_input": today[1],
                "today_output": today[2],
                "today_total": today[1] + today[2],
                "today_cost": today[3],
            }
        return None
    except Exception as e:
        return {"error": str(e)}


def get_rtk():
    try:
        r = subprocess.run(
            ["rtk", "gain", "--daily", "--format", "json"],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
    except:
        pass
    return None


def get_errors():
    """Get real errors (not warnings) and translate them."""
    if not os.path.exists(ERROR_LOG):
        return []
    try:
        # Get lines with ERROR or CRITICAL or FAILED or Traceback
        r = subprocess.run(
            f"tail -100 {ERROR_LOG} | grep -iE '\\b(ERROR|CRITICAL|FAILED|Traceback|Exception)\\b'",
            shell=True, capture_output=True, text=True, timeout=10
        )
        lines = [l.strip() for l in r.stdout.split("\n") if l.strip()]
        
        # Translate to plain Indonesian
        translated = []
        for line in lines[-5:]:
            translated.append(_translate_error(line))
        return translated
    except:
        return []


def _translate_error(raw):
    """Translate raw error log to plain Indonesian."""
    raw_lower = raw.lower()
    
    if "tool" in raw_lower and ("returned" in raw_lower or "error" in raw_lower):
        tool_name = ""
        if "read_file" in raw:
            tool_name = "baca file"
        elif "write_file" in raw:
            tool_name = "nulis file"
        elif "cronjob" in raw or "cron" in raw_lower:
            tool_name = "jadwal tugas"
        elif "terminal" in raw:
            tool_name = "jalanin perintah"
        elif "patch" in raw:
            tool_name = "edit file"
        elif "search" in raw_lower:
            tool_name = "cari data"
        elif "send" in raw_lower:
            tool_name = "kirim pesan"
        else:
            tool_name = "proses"
        return f"❌ Gagal {tool_name}, coba ulang nanti"

    if "connection" in raw_lower or "timeout" in raw_lower or "network" in raw_lower:
        return "🌐 Gagal konek ke server, cek internet"
    
    if "memory" in raw_lower or "oom" in raw_lower:
        return "💥 RAM abis! Proses terpaksa dimatiin"
    
    if "disk" in raw_lower or "space" in raw_lower or "no space" in raw_lower:
        return "💾 Storage penuh!"
    
    if "permission" in raw_lower or "denied" in raw_lower or "forbidden" in raw_lower:
        return "🔒 Ga punya akses, perlu izin lebih"
    
    if "not found" in raw_lower or "no such" in raw_lower:
        return "🔍 File atau folder ga ditemukan"
    
    if "rate" in raw_lower and "limit" in raw_lower:
        return "⏳ Kecepatan limit, tunggu sebentar"
    
    if "auth" in raw_lower or "unauthorized" in raw_lower or "token" in raw_lower:
        return "🔑 Token/login bermasalah, perlu login ulang"
    
    # Generic fallback
    short = raw[:80]
    return f"⚠️ `{short}...`"


def main():
    lines = []
    lines.append("━━━ **📊 DAILY BRIEFING** ━━━")
    lines.append(f"`{WIB}`")
    lines.append("")

    # ── Tokens ──
    lines.append("**💎 Token Usage**")
    t = get_tokens()
    if t and "error" not in t:
        def fmt(n):
            if n >= 1_000_000:
                return f"{n/1_000_000:.1f}jt"
            elif n >= 1_000:
                return f"{n/1_000:.1f}k"
            return str(n)
        
        lines.append(f"`24h ` {t['sessions']} sesi · {t['messages']} pesan")
        lines.append(f"`In  ` {fmt(t['input'])} → `Out` {fmt(t['output'])}")
        lines.append(f"`Total` **{fmt(t['total'])}** token")
        cost_str = f"${t['cost']:.6f}"
        lines.append(f"`Cost` 💰 {cost_str}")
        
        if t['today_sessions'] > 0:
            lines.append(f"`Hari` {t['today_sessions']} ses · **{fmt(t['today_total'])}** tok · ${t['today_cost']:.6f}")
    elif t and "error" in t:
        lines.append(f"`   `⚠️ Error baca data: {t['error']}")
    else:
        lines.append("`   `📭 Belum ada aktivitas hari ini")
    lines.append("")

    # ── RTK ──
    lines.append("**💚 RTK Hemat**")
    rtk = get_rtk()
    if rtk and "summary" in rtk:
        s = rtk["summary"]
        pct = f"{s['avg_savings_pct']:.0f}%"
        lines.append(f"`   `{s['total_commands']} command diproses")
        lines.append(f"`   `{s['total_input']:,} → {s['total_output']:,} token")
        lines.append(f"`   `**Hemat {s['total_saved']:,} token ({pct})**")
    else:
        lines.append("`   `📭 Belum ada data RTK")
    lines.append("")

    # ── Errors ──
    errs = get_errors()
    lines.append("**⚠️ Error Log**")
    if errs:
        for e in errs:
            lines.append(f"`   `{e}")
    else:
        lines.append("`   `✅ Lancar, ga ada error")
    lines.append("")

    lines.append("━━━━━━━━━━━━━━━━━━━")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
