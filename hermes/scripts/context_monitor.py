#!/usr/bin/env python3
"""📊 Context Monitor — ngasih tau kalo session Hermes mulai penuh."""
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from error_log import ErrorLog

DB = os.path.expanduser("~/.hermes/state.db")
STATE_FILE = os.path.expanduser("~/.hermes/scripts/.context_thresholds.json")
AMBANG_PCT = [2.5, 5, 10, 25, 50, 75, 90]

log = ErrorLog("📊 Session Deck")

KAPASITAS = {
    "deepseek/deepseek-v4": 1_000_000, "deepseek/deepseek-v3": 1_000_000,
    "deepseek/deepseek-r1": 1_000_000, "deepseek/deepseek-chat": 64_000,
    "claude": 200_000, "gpt-4.1": 1_000_000, "gpt-4o": 128_000,
    "gemini-2.5-pro": 1_000_000, "gemini-2.5-flash": 1_000_000,
    "gemini-2.0-flash": 1_048_576, "gemini-1.5-pro": 2_000_000,
    "llama-4": 1_000_000, "llama-3.1": 128_000,
    "mistral-large": 128_000, "codestral": 256_000,
    "qwen-2.5": 128_000, "mimo": 128_000, "nova": 128_000,
}


def cari_kapasitas(model: str) -> int:
    if not model:
        return 128_000
    m = model.lower()
    for key in sorted(KAPASITAS.keys(), key=len, reverse=True):
        if key in m:
            return KAPASITAS[key]
    return 128_000


def ikon_session(sid: str) -> str:
    s = sid.lower()
    if "cron" in s: return "⏰"
    if "subagent" in s: return "🤖"
    if "cli" in s: return "💻"
    return "💬"


def main():
    ok_items = []

    if not os.path.exists(DB):
        log.info("Belum ada database", "Hermes belum pernah dipakai atau DB gak ditemukan")
        return finalize()

    # ── Load state ──
    notified = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                notified = json.load(f).get("notified", {})
        except:
            notified = {}

    # ── Query DB ──
    try:
        conn = sqlite3.connect(DB, timeout=5)
        cur = conn.execute("""
            SELECT id, COALESCE(title,'untitled'), COALESCE(model,''),
                   COALESCE(input_tokens + output_tokens, 0)
            FROM sessions
            WHERE ended_at IS NULL
               OR started_at > strftime('%%s', 'now', '-24 hours')
            ORDER BY (input_tokens + output_tokens) DESC
        """)
        rows = cur.fetchall()
        conn.close()
    except sqlite3.Error as e:
        log.error("Gagal baca database", f"Error SQLite: {e}", "Cek file state.db")
        return finalize()

    if not rows:
        log.ok("Gak ada session aktif")
        return finalize()

    active_count = sum(1 for r in rows if r[3] and r[3] > 1000)
    log.ok(f"{len(rows)} session ({active_count} aktif)")
    new_alerts = []
    dirty = False
    model_unknown = 0

    for sid, title, model, total in rows:
        total = total or 0
        if total < 1000:
            continue

        kap = cari_kapasitas(model)
        if kap <= 0:
            model_unknown += 1
            kap = 128_000

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
            icon = ikon_session(sid)
            model_short = model.split("/")[-1] if model else "?"
            kap_str = f"{kap:,}" if kap >= 1_000 else str(kap)

            baris = f"{icon} **{max_pct}%** ({total:,}/{kap_str}) — `{model_short}`"
            baris2 = f"  _{title_short}_"
            if max_pct >= 90:
                baris2 += "\n  ⚠️ **Hampir full!** Ketik `/compress`"
                log.warning("Session mau penuh", f"'{title_short}' {pct}%", "Ketik /compress sekarang")
            elif max_pct >= 75:
                baris2 += "\n  ⚠️ Mending /compress biar gak penuh"
                log.info("Session lumayan penuh", f"'{title_short}' {pct}%")

            new_alerts.append(f"{baris}\n{baris2}")

            notified[sid] = sorted(set(ses_notified + baru))
            dirty = True

    if model_unknown > 0:
        log.info(f"Ada {model_unknown} session model baru", "Kalo sering muncul, tambahin ke daftar kapasitas")

    if new_alerts:
        print("📊 **Session Deck** — session mulai penuh:\n")
        print("\n\n".join(new_alerts))
        print()

    if dirty:
        try:
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            with open(STATE_FILE, 'w') as f:
                json.dump({"notified": notified}, f)
        except OSError:
            log.error("Gagal simpan data", "State file gak bisa ditulis", "Cek disk")

    finalize(active_count)


def finalize(active=0):
    # Status table
    from datetime import datetime

    total_all = active if active > 0 else 1
    lines = [f"✅ **📊 Session Deck**\n"]
    lines.append("| Item | Jumlah |")
    lines.append("|------|--------|")
    lines.append(f"| Session aktif | {total_all} |")
    lines.append("")
    lines.append(f"🕐 {datetime.now().strftime('%a %d %b %H:%M')}")

    err_report = log.format_report()
    if err_report and log.ada_masalah():
        lines.append("")
        lines.append(err_report)

    print("\n".join(lines))
    log.persist()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("Error gak terduga", "Coba jalankan ulang")
        finalize()
