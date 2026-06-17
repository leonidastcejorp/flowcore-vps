#!/usr/bin/env python3
"""
🎨 Telegram UI Kit — format notifikasi cron & monitoring buat Telegram.
Wajib pakai Markdown table, tanpa bullet points.
"""
from __future__ import annotations

import socket
from datetime import datetime


def severity_icon(level: str) -> str:
    return {
        "CRITICAL": "💀",
        "ERROR": "🔴",
        "WARNING": "🟡",
        "INFO": "ℹ️",
        "OK": "✅",
    }.get(level.upper(), "⚪")


def progress_bar(pct: float, width: int = 8) -> str:
    pct = max(0.0, min(100.0, pct))
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


def human_bytes(value: str | float | int) -> str:
    """Coba parse nilai byte jadi human readable."""
    try:
        n = float(value)
    except (ValueError, TypeError):
        return str(value)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


class TelegramMessage:
    """Builder buat pesan Telegram dengan gaya konsisten."""

    def __init__(self, title: str, icon: str, level: str = "OK"):
        self.title = title
        self.icon = icon
        self.level = level
        self._parts: list[str] = []
        self._has_content = False
        self._header()

    def _header(self):
        ts = datetime.now().strftime("%a %d %b %H:%M WIB")
        host = socket.gethostname()
        level_ico = severity_icon(self.level)
        title = f"{self.icon} {self.title}".strip() if self.icon else self.title
        self._parts.append(f"{level_ico} **{title}**")
        self._parts.append(f"`{host}`  \u00b7  `{ts}`")
        self._parts.append("")

    def add_text(self, text: str):
        self._parts.append(text)
        self._has_content = True

    def add_alert(self, level: str, title: str, detail: str, recommendation: str = ""):
        ico = severity_icon(level)
        self._parts.append(f"{ico} **{title}**")
        if detail:
            self._parts.append(f"  {detail}")
        if recommendation:
            self._parts.append(f"  → {recommendation}")
        self._parts.append("")
        self._has_content = True

    def add_table(self, headers: list[str], rows: list[list[str]]):
        if not rows:
            return
        lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
        for row in rows:
            # escape pipe inside cell? just replace
            safe = [str(c).replace("|", "/") for c in row]
            lines.append("| " + " | ".join(safe) + " |")
        self._parts.append("\n".join(lines))
        self._parts.append("")
        self._has_content = True

    def add_metric(self, label: str, value: str, pct: float | None = None):
        if pct is not None:
            bar = progress_bar(pct)
            self._parts.append(f"`{bar}`  **{label}:** {value}  ({pct:.0f}%)")
        else:
            self._parts.append(f"**{label}:** {value}")
        self._has_content = True

    def add_footer(self):
        self._parts.append("🕐 " + datetime.now().strftime("%a %d %b %H:%M"))

    def render(self) -> str:
        self.add_footer()
        return "\n".join(self._parts).strip()

    @property
    def has_content(self) -> bool:
        return self._has_content


def empty() -> str:
    """Untuk no_agent cron: stdout kosong = notifikasi silent."""
    return ""
