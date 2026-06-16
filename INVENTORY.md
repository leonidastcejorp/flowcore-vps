# INVENTORY.md — Complete File Manifest

> **FlowCore VPS Backup Repository**
> Total files: 58 (+ .git internal)

---

## ROOT FILES (7 files)

| # | Path | Size | Description |
|---|------|------|-------------|
| 1 | `setup.sh` | 19.7 KB | **Main setup script** — installs everything (10-15 min) |
| 2 | `pre-flight.sh` | 4.3 KB | **Pre-flight check** — cek VPS siap sebelum setup |
| 3 | `deploy-cron.sh` | 7.2 KB | **Deploy 12 cron jobs** — NO-AGENT mode, Telegram + local |
| 4 | `CONFIG_REFERENCE.md` | 18.0 KB | **Config reference** — semua section config.yaml dijelasin |
| 5 | `SUMMARY.md` | 6.2 KB | **Tools & dependencies** — versi, install method, links |
| 6 | `README.md` | 1.5 KB | Repo docs |
| 7 | `INVENTORY.md` | ~6 KB | This file — complete manifest |

## HERMES AGENT — Config & Personality (4 files)

| # | Path | Size | Description |
|---|------|------|-------------|
| 8 | `hermes/config.yaml` | 9.5 KB | **Main config** — API keys redacted, model: deepseek/deepseek-v4-flash |
| 9 | `hermes/SOUL.md` | 8.7 KB | **BREACH v3.0** — Unrestricted agent personality |
| 10 | `hermes/SOUL.backup.md` | 0.5 KB | Default Hermes personality backup |
| 11 | `hermes/state.db` | 5.4 MB | Hermes state database (sessions, tokens, costs) |

## HERMES SCRIPTS (15 files)

| # | Path | Size | Description |
|---|------|------|-------------|
| 12 | `hermes/scripts/monitor.py` | 7.4 KB | **🚨 FBI Watchdog** — RAM/CPU/Disk/uptime monitor |
| 13 | `hermes/scripts/daily_report.py` | 13.1 KB | **📊 FBI Daily Briefing** — Token usage, errors, recommendations |
| 14 | `hermes/scripts/income_pipeline.py` | 8.5 KB | **💰 CuanFeed** — Freelance & airdrop opportunities |
| 15 | `hermes/scripts/proxy_updater.py` | 6.4 KB | **🔁 Proxy Pool** — Download + test free proxies |
| 16 | `hermes/scripts/prune.sh` | 0.3 KB | **🧹 Session Prune** — Hapus sessions >30 hari |
| 17 | `hermes/scripts/context_monitor.py` | 5.6 KB | **📈 LogDesk** — Pantau session Hermes mulai penuh |
| 18 | `hermes/scripts/disk_alert.sh` | 3.3 KB | **💾 DiskBay** — Cek storage & swap (silent kalo aman) |
| 19 | `hermes/scripts/error_summary.py` | 3.4 KB | **📋 Briefing** — Kumpulin error dari semua monitor |
| 20 | `hermes/scripts/memory_monitor.py` | 6.4 KB | **📈 MemStat** — Pantau RAM & swap pressure |
| 21 | `hermes/scripts/ssh_attack_monitor.py` | 5.9 KB | **🚪 PortGuard** — Deteksi brute-force SSH |
| 22 | `hermes/scripts/reboot_monitor.py` | 5.3 KB | **🔁 Bootmark** — Deteksi VPS restart tiba-tiba |
| 23 | `hermes/scripts/vps_backup.sh` | 3.5 KB | **📦 Backup** — Weekly backup Hermes config + projects |
| 24 | `hermes/scripts/lib/error_log.py` | 9.4 KB | **Lib** — Error logging library (Python) |
| 25 | `hermes/scripts/lib/error_log.sh` | 3.9 KB | **Lib** — Error logging library (Shell) |
| 26 | `hermes/cron/jobs.json` | 14.8 KB | **Cron schedule** — 12 jobs: Telegram group + local |

## RTK PLUGIN (2 files)

| # | Path | Size | Description |
|---|------|------|-------------|
| 27 | `hermes/plugins/rtk-rewrite/__init__.py` | 2.4 KB | RTK pre-tool-call hook — rewrite terminal commands |
| 28 | `hermes/plugins/rtk-rewrite/plugin.yaml` | 0.2 KB | Plugin metadata |

## SSH KEYS (2 files)

| # | Path | Size | Description |
|---|------|------|-------------|
| 29 | `ssh/id_ed25519` | 0.4 KB | **🔴 SENSITIVE** — Ed25519 private key |
| 30 | `ssh/id_ed25519.pub` | 0.1 KB | SSH public key |

## FLOWCORE TOOLKIT (20 files)

| # | Path | Size | Description |
|---|------|------|-------------|
| 31 | `tools/flowcore/README.md` | 2.7 KB | Framework docs |
| 32 | `tools/flowcore/LICENSE` | 1.0 KB | MIT License |
| 33 | `tools/flowcore/setup.py` | 0.5 KB | Python package setup |
| 34 | `tools/flowcore/requirements.txt` | 0.1 KB | Dependencies |
| 35 | `tools/flowcore/config/config.yaml` | 0.9 KB | Framework config |
| 36 | `tools/flowcore/scripts/run_pipeline.py` | 0.3 KB | Pipeline runner |
| 37 | `tools/flowcore/scripts/refresh_proxies.py` | 0.6 KB | Proxy pool refresh |
| 38 | `tools/flowcore/tests/test_browser.py` | 0.9 KB | Test suite |
| 39 | `tools/flowcore/docs/TUTORIAL.md` | 8.3 KB | FlowCore tutorial |
| 40 | `tools/flowcore/flowcore/__init__.py` | 0 B | Package init |
| 41 | `tools/flowcore/flowcore/core/__init__.py` | 0 B | Core init |
| 42 | `tools/flowcore/flowcore/core/browser.py` | 5.2 KB | Playwright wrapper |
| 43 | `tools/flowcore/flowcore/core/fingerprint.py` | 1.9 KB | Identity generator |
| 44 | `tools/flowcore/flowcore/modules/__init__.py` | 0 B | Modules init |
| 45 | `tools/flowcore/flowcore/modules/registrar.py` | 7.4 KB | Form automation |
| 46 | `tools/flowcore/flowcore/modules/scraper.py` | 1.6 KB | Web scraper |
| 47 | `tools/flowcore/flowcore/modules/watcher.py` | 3.8 KB | Pipeline monitoring |
| 48 | `tools/flowcore/flowcore/utils/__init__.py` | 0 B | Utils init |
| 49 | `tools/flowcore/flowcore/utils/names.py` | 2.0 KB | Name generator |
| 50 | `tools/flowcore/flowcore/utils/network.py` | 3.2 KB | Proxy manager |

## STANDALONE TOOLS (6 files)

| # | Path | Size | Description |
|---|------|------|-------------|
| 51 | `tools/ghost_creator.py` | 14.1 KB | **🔥 GHOST v1.0** — Mass account creator |
| 52 | `tools/ghost_tester.py` | 6.8 KB | **🔥 Turnstile Bypass** — Test Cloudflare bypass |
| 53 | `tools/income_pipeline.py` | 7.1 KB | Income pipeline (duplicate of #14) |
| 54 | `tools/farming_guide.py` | 5.4 KB | **🌐 Airdrop guide** — Faucets, platforms, earnings |
| 55 | `tools/airdrop_monitor.py` | 4.6 KB | **📡 Airdrop monitor** — Galxe, Layer3, Reddit |
| 56 | `tools/README.md` | 2.9 KB | Tools directory docs |

## DATA (1 file)

| # | Path | Size | Description |
|---|------|------|-------------|
| 57 | `data/subdomains_raw.txt` | 39 KB | Bug bounty subdomains — Tokopedia & Bukalapak |

## TUTORIAL (1 file)

| # | Path | Size | Description |
|---|------|------|-------------|
| 58 | `TUTORIAL.md` | 11.4 KB | Complete usage guide (Bahasa Indonesia campur Inggris) |

## FILE STATISTICS

| Category | Count | Total Size |
|----------|-------|------------|
| Python scripts | 22 | ~170 KB |
| Shell scripts | 6 | ~42 KB |
| YAML config | 4 | ~28 KB |
| JSON data | 1 | ~15 KB |
| SQLite DB | 1 | 5.4 MB |
| SSH keys | 2 | ~0.5 KB |
| Markdown docs | 8 | ~57 KB |
| Text data | 2 | ~40 KB |
| Text/LICENSE | 1 | ~1 KB |
| Package init | 5 | 0 B |
| Config ref | 1 | ~18 KB |
| **Total** | **58** | **~319 KB + state.db (5.4 MB)** |

## CRON SCHEDULE SUMMARY — 12 Jobs

| # | Job | Script | Schedule | Deliver |
|---|-----|--------|----------|---------|
| 1 | 🚨 FBI Watchdog | `monitor.py` | every 360m | Telegram group |
| 2 | 📊 FBI Daily Briefing | `daily_report.py` | 0 16 * * * | Telegram group |
| 3 | 🧹 Hermes Session Prune | `prune.sh` | 0 3 * * 1 | Local |
| 4 | 💰 Income Pipeline (CuanFeed) | `income_pipeline.py` | every 360m | Telegram group |
| 5 | 🔁 Proxy Auto-Updater | `proxy_updater.py` | every 360m | Local |
| 6 | 📦 VPS Weekly Backup | `vps_backup.sh` | 0 2 * * 0 | Local |
| 7 | 💾 Disk Usage Watchdog (DiskBay) | `disk_alert.sh` | every 360m | Telegram group |
| 8 | 📈 Context Monitor (LogDesk) | `context_monitor.py` | every 60m | Telegram group |
| 9 | 🚪 SSH Attack Monitor (PortGuard) | `ssh_attack_monitor.py` | every 360m | Telegram group |
| 10 | 🔁 Reboot Monitor (Bootmark) | `reboot_monitor.py` | every 15m | Telegram group |
| 11 | 📈 Memory Pressure Monitor (MemStat) | `memory_monitor.py` | every 60m | Telegram group |
| 12 | 📋 Error Log Summary (Briefing) | `error_summary.py` | every 360m | Telegram group |

**Delivery**: 8 → Telegram group Kantor FBI (`-1003534226714`), 3 → Local, 1 → Briefing.
**All jobs NO-AGENT mode** — gak pake LLM, langsung jalanin script.
