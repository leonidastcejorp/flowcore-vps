#!/usr/bin/env python3
"""📊 ContextMon — ngasih tau kalo session Hermes mulai penuh."""
import json
import os
import sqlite3
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from error_log import ErrorLog

DB = os.path.expanduser("~/.hermes/state.db")
STATE_FILE = os.path.expanduser("~/.hermes/scripts/.context_thresholds.json")
AMBANG_PCT = [2.5, 5, 10, 25, 50, 75, 90]
log = ErrorLog("📊 ContextMon")

KAPASITAS = {
    "deepseek/deepseek-v4": 1_000_000, "deepseek/deepseek-v3": 1_000_000,
    "deepseek/deepseek-r1": 1_000_000, "deepseek/deepseek-chat": 64_000,
    "claude": 200_000, "gpt-4.1": 1_000_000, "gpt-4o": 128_000,
    "gemini": 1_000_000, "llama-4": 1_000_000, "llama-3.1": 128_000,
    "mistral-large": 128_000, "codestral": 256_000, "qwen-2.5": 128_000,
}


def cari_kapasitas(model: str) -> int:
    if not model:
        return 128_000
    m = model.lower()
    for key in sorted(KAPASITAS.keys(), key=len, reverse=True):
        if key in m:
            return KAPASITAS[key]
    return 128_000


def main():
    lines = []

    if not os.path.exists(DB):
        lines.append("✅ 📊 ContextMon")
        lines.append("")
        lines.append("Status")
        lines.append("• Gak ada database — Hermes belum pernah dipakai")
        lines.append("")
        lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
        log.persist()
        print("\n".join(lines))
        return

    notified = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                notified = json.load(f).get("notified", {})
        except:
            notified = {}

    try:
        conn = sqlite3.connect(DB, timeout=5)
        cur = conn.execute("""
            SELECT id, COALESCE(title,'untitled'), COALESCE(model,''),
                   COALESCE(input_tokens + output_tokens, 0)
            FROM sessions
            WHERE ended_at IS NULL OR started_at > strftime('%%s', 'now', '-24 hours')
            ORDER BY (input_tokens + output_tokens) DESC
        """)
        rows = cur.fetchall()
        conn.close()
    except sqlite3.Error as e:
        log.error("Gagal baca database", f"Error: {e}", "Cek file state.db")
        lines.append("✅ 📊 ContextMon")
        lines.append("")
        lines.append("Status")
        lines.append(f"• Error baca database: {e}")
        lines.append("")
        lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
        log.persist()
        print("\n".join(lines))
        return

    if not rows:
        lines.append("✅ 📊 ContextMon")
        lines.append("")
        lines.append("Status")
        lines.append("• Gak ada session aktif")
        lines.append("")
        lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
        log.persist()
        print("\n".join(lines))
        return

    active = sum(1 for r in rows if r[3] and r[3] > 1000)
    new_alerts = []
    dirty = False

    for sid, title, model, total in rows:
        total = total or 0
        if total < 1000:
            continue
        kap = cari_kapasitas(model)
        pct = int(total * 100 / kap)
        title_short = (title or "untitled")[:45]
        ses_notified = notified.get(sid, [])

        baru = []
        for ambang in AMBANG_PCT:
            t_abs = int(kap * ambang / 100)
            if total >= t_abs and ambang not in ses_notified:
                baru.append(ambang)

        if baru:
            max_pct = max(baru)
            model_short = model.split("/")[-1] if model else "?"
            kap_str = f"{kap:,}"

            lines2 = []
            lines2.append(f"Session: _{title_short}_")
            lines2.append(f"• Kapasitas: {max_pct}% ({total:,}/{kap_str})")
            lines2.append(f"• Model: {model_short}")
            if max_pct >= 90:
                lines2.append(f"• Saran: **Ketik /compress — hampir full!**")
                log.warning("Session mau penuh", f"'{title_short}' {pct}%", "Ketik /compress")
            elif max_pct >= 75:
                lines2.append(f"• Saran: Mending /compress")
                log.info("Session lumayan penuh", f"'{title_short}' {pct}%")
            new_alerts.append("\n".join(lines2))

            notified[sid] = sorted(set(ses_notified + baru))
            dirty = True

    if not new_alerts:
        lines.append("✅ 📊 ContextMon")
        lines.append("")
        lines.append("Status")
        lines.append(f"• {len(rows)} session ({active} aktif) — semua aman")
        lines.append("")
        lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
    else:
        lines.append(f"🟡 📊 ContextMon")
        lines.append("")
        for a in new_alerts:
            lines.append(a)
            lines.append("")
        err_report = log.format_report()
        if err_report:
            lines.append(err_report)
            lines.append("")
        lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")

    if dirty:
        try:
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            with open(STATE_FILE, 'w') as f:
                json.dump({"notified": notified}, f)
        except OSError:
            log.error("Gagal simpan data", "State file gak bisa ditulis", "Cek disk")

    log.persist()
    print("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("Error gak terduga", "Coba jalankan ulang")
        print(f"✅ 📊 ContextMon\n\nStatus\n• —\n\n🕐 {datetime.now().strftime('%a %d %b %H:%M')}")
