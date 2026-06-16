#!/usr/bin/env python3
"""
🔧 BREACH Error Log — shared error logging for all monitor scripts.
Centralized JSON error log with human-friendly Telegram output.

Usage:
    from lib.error_log import ErrorLog

    log = ErrorLog("📈 Memory Monitor")
    log.error("Gagal baca log kernel", "Butuh akses khusus sistem", "Biar gua kasih akses?")
    log.ok("RAM normal", "32% (647MB)")

    # At script exit, if there were errors:
    #   print(log.format_report())  → clean human message for Telegram
    # The calling script prints this to stdout (no_agent mode) for delivery.
"""

import json
import os
import sys
import traceback
from datetime import datetime

ERROR_LOG_PATH = os.path.expanduser("~/.hermes/scripts/.error_log.json")
MAX_ENTRIES = 500
WIB = lambda: datetime.now().strftime("%Y-%m-%d %H:%M WIB")
WIB_SHORT = lambda: datetime.now().strftime("%a %d %b %H:%M")


class ErrorLog:
    def __init__(self, display_name: str):
        """display_name: Nama yang muncul di notifikasi, contoh '📈 Memory Monitor'"""
        self.display_name = display_name
        self.script_name = display_name.replace(" ", "_").lower()[:32]
        self.entries: list[dict] = []
        self.ok_messages: list[str] = []  # ✅ status items (shown in report)

    def _add(self, level: str, judul: str, detail: str, saran: str = ""):
        """Internal: add an entry."""
        self.entries.append({
            "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "script": self.script_name,
            "display_name": self.display_name,
            "level": level,
            "judul": judul[:80],
            "detail": detail[:250],
            "saran": saran[:200],
        })

    def critical(self, judul: str, detail: str, saran: str = ""):
        """💀 Bahaya — butuh tindakan segera."""
        self._add("CRITICAL", judul, detail, saran)

    def error(self, judul: str, detail: str, saran: str = ""):
        """🔴 Error — ada masalah, script tetep jalan."""
        self._add("ERROR", judul, detail, saran)

    def warning(self, judul: str, detail: str, saran: str = ""):
        """🟡 Warning — kondisi gak biasa, perlu dipantau."""
        self._add("WARNING", judul, detail, saran)

    def info(self, judul: str, detail: str):
        """ℹ️ Info — catatan aja."""
        self._add("INFO", judul, detail)

    def ok(self, judul: str, detail: str = ""):
        """✅ Status baik — ditampilkan di footer report."""
        if detail:
            self.ok_messages.append(f"{judul} · {detail}")
        else:
            self.ok_messages.append(judul)

    def exception(self, judul: str = "Script crash", saran: str = ""):
        """Log current Python exception."""
        exc_type, exc_value, _ = sys.exc_info()
        detail = f"{exc_type.__name__}: {exc_value}" if exc_value else "Error gak dikenal"
        tb = traceback.format_exc()
        self._add("ERROR", judul, detail, saran)

    # ── Reporting ──────────────────────────────────────────────────────────

    def ada_masalah(self) -> bool:
        """True if there are CRITICAL, ERROR, or WARNING entries."""
        for e in self.entries:
            if e["level"] in ("CRITICAL", "ERROR", "WARNING"):
                return True
        return False

    def format_report(self) -> str | None:
        """
        Format semua entry jadi pesan Telegram yang bersih & manusiawi.
        Output None kalo aman semua (silent).
        """
        if not self.entries and not self.ok_messages:
            return None

        has_issues = self.ada_masalah()
        lines = []

        # ── Header ──
        header_icon = "💀" if any(e["level"] == "CRITICAL" for e in self.entries) else \
                      "🔴" if any(e["level"] == "ERROR" for e in self.entries) else \
                      "🟡" if any(e["level"] == "WARNING" for e in self.entries) else \
                      "✅"
        lines.append(f"{header_icon} **{self.display_name}**")
        lines.append("")

        # ── Bad entries (CRITICAL → ERROR → WARNING) ──
        shown_any_bad = False
        for level, icon in [("CRITICAL", "💀"), ("ERROR", "🔴"), ("WARNING", "🟡")]:
            lev_entries = [e for e in self.entries if e["level"] == level]
            if not lev_entries:
                continue
            shown_any_bad = True

            for e in lev_entries:
                lines.append(f"{icon} **{e['judul']}**")
                if e["detail"]:
                    # Wrap detail in bullet
                    lines.append(f"  {e['detail']}")
                if e["saran"]:
                    lines.append(f"  → {e['saran']}")
                lines.append("")

        # ── OK messages ──
        if self.ok_messages:
            for msg in self.ok_messages:
                lines.append(f"✅ {msg}")
            lines.append("")

        # ── Footer ──
        lines.append(f"🕐 {WIB_SHORT()}")

        return "\n".join(lines).rstrip()

    def format_error_only(self) -> str | None:
        """
        Format cuma error/warning entries, tanpa OK messages.
        Buat daily briefing / error summary.
        """
        bad = [e for e in self.entries if e["level"] in ("CRITICAL", "ERROR", "WARNING")]
        if not bad:
            return None

        lines = []
        for level, icon in [("CRITICAL", "💀"), ("ERROR", "🔴"), ("WARNING", "🟡")]:
            lev = [e for e in bad if e["level"] == level]
            for e in lev:
                lines.append(f"{icon} **{e['judul']}**")
                lines.append(f"  {e['detail']}")
                if e.get("saran"):
                    lines.append(f"  → {e['saran']}")
                lines.append("")

        return "\n".join(lines).rstrip()

    def persist(self):
        """Save entries ke file error log pusat."""
        existing = []
        if os.path.exists(ERROR_LOG_PATH):
            try:
                with open(ERROR_LOG_PATH) as f:
                    existing = json.load(f)
            except (json.JSONDecodeError, OSError):
                existing = []

        existing.extend(self.entries)

        if len(existing) > MAX_ENTRIES:
            existing = existing[-MAX_ENTRIES:]

        os.makedirs(os.path.dirname(ERROR_LOG_PATH), exist_ok=True)
        with open(ERROR_LOG_PATH, "w") as f:
            json.dump(existing, f, indent=2)

    # ── Static: Read & Format ──────────────────────────────────────────────

    @staticmethod
    def get_recent(limit: int = 20) -> list[dict]:
        """Ambil entry terbaru dari error log."""
        if not os.path.exists(ERROR_LOG_PATH):
            return []
        try:
            with open(ERROR_LOG_PATH) as f:
                data = json.load(f)
            return data[-limit:]
        except (json.JSONDecodeError, OSError):
            return []

    @staticmethod
    def format_summary(limit: int = 10) -> str | None:
        """
        Format ringkasan error buat daily briefing / error summary cron.
        Output: clean human format.
        """
        entries = ErrorLog.get_recent(limit)
        if not entries:
            return None

        crit = [e for e in entries if e["level"] == "CRITICAL"]
        errs = [e for e in entries if e["level"] == "ERROR"]
        warns = [e for e in entries if e["level"] == "WARNING"]

        total_masalah = len(crit) + len(errs) + len(warns)
        if total_masalah == 0:
            return None

        # Group by display name
        by_name = {}
        for e in crit + errs + warns:
            name = e.get("display_name", e.get("script", "?"))
            if name not in by_name:
                by_name[name] = []
            by_name[name].append(e)

        lines = []
        header_icon = "💀" if crit else "🔴"
        total_all = len(crit) + len(errs) + len(warns)

        lines.append(f"{header_icon} Ada **{total_all} hal** perlu diperhatikan:\n")

        for name in sorted(by_name.keys()):
            items = by_name[name]
            worst = max((e["level"] for e in items), key=lambda l: ["INFO", "WARNING", "ERROR", "CRITICAL"].index(l))
            icon = {"CRITICAL": "💀", "ERROR": "🔴", "WARNING": "🟡"}.get(worst, "🟡")

            lines.append(f"{icon} **{name}**")
            for e in items:
                lines.append(f"  • {e['judul']}")
                if e.get("saran"):
                    lines.append(f"    → {e['saran']}")
            lines.append("")

        lines.append(f"🕐 {WIB_SHORT()}")
        return "\n".join(lines)

    @staticmethod
    def clear_old(days: int = 14):
        """Hapus entry yang lebih lama dari N hari."""
        if not os.path.exists(ERROR_LOG_PATH):
            return
        try:
            with open(ERROR_LOG_PATH) as f:
                data = json.load(f)
            cutoff = datetime.now().timestamp() - (days * 86400)
            data = [e for e in data if datetime.strptime(e["ts"], "%Y-%m-%d %H:%M:%S").timestamp() > cutoff]
            with open(ERROR_LOG_PATH, "w") as f:
                json.dump(data, f, indent=2)
        except (json.JSONDecodeError, OSError, ValueError, KeyError):
            pass
