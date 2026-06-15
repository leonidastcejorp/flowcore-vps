# 📋 INVENTORY.md — Complete File Manifest

> **FlowCore VPS Backup Repository**
> Total files: 52 (+ directories)

---

## 🔧 HERMES AGENT CONFIGURATION (10 files)

| # | Path | Type | Size | Description |
|---|------|------|------|-------------|
| 1 | `hermes/config.yaml` | YAML | ~17KB | **Main Hermes config** — API keys redacted, all settings intact |
| 2 | `hermes/SOUL.md` | Markdown | ~8.7KB | **BREACH v3.0 UNRESTRICTED** — Full adversarial agent personality |
| 3 | `hermes/SOUL.backup.md` | Markdown | ~0.5KB | Default Hermes personality backup (template only) |
| 4 | `hermes/state.db` | SQLite | ~varies | Hermes state database (sessions, tokens, costs) |
| 5 | `hermes/scripts/monitor.py` | Python | ~5KB | **📡 FBI Watchdog** — RAM/CPU/Disk monitor, silent when clear |
| 6 | `hermes/scripts/income_pipeline.py` | Python | ~7KB | **💰 Income Pipeline** — Reddit/crypto/freelance opportunity scraper |
| 7 | `hermes/scripts/proxy_updater.py` | Python | ~3.4KB | **🔄 Proxy Auto-Updater** — Downloads+tests free proxies from GitHub |
| 8 | `hermes/scripts/daily_report.py` | Python | ~7.2KB | **📊 Daily Briefing** — Token usage, RTK savings, error translation |
| 9 | `hermes/scripts/prune.sh` | Shell | ~0.2KB | **🧹 Session Pruner** — Deletes sessions older than 30 days |
| 10 | `hermes/cron/jobs.json` | JSON | ~6KB | **Cron schedule** — 5 jobs: watchdog, briefing, prune, pipeline, proxy |

## 🔌 RTK REWRITE PLUGIN (2 files)

| # | Path | Type | Size | Description |
|---|------|------|------|-------------|
| 11 | `hermes/plugins/rtk-rewrite/__init__.py` | Python | ~2.4KB | RTK pre-tool-call hook — rewrites terminal commands |
| 12 | `hermes/plugins/rtk-rewrite/plugin.yaml` | YAML | ~0.2KB | Plugin metadata and hook declarations |

## 🔑 SSH KEYS (2 files)

| # | Path | Type | Size | Description |
|---|------|------|------|-------------|
| 13 | `ssh/id_ed25519` | Private Key | ~0.4KB | **🔴 SENSITIVE** — Ed25519 SSH private key (flowcore@leonidas) |
| 14 | `ssh/id_ed25519.pub` | Public Key | ~0.1KB | SSH public key |

## 🧰 FLOWCORE TOOLKIT — Full Framework (20 files)

| # | Path | Type | Size | Description |
|---|------|------|------|-------------|
| 15 | `tools/flowcore/README.md` | Markdown | ~2.7KB | Framework documentation and quick start |
| 16 | `tools/flowcore/LICENSE` | Text | ~1KB | MIT License |
| 17 | `tools/flowcore/setup.py` | Python | ~0.5KB | Python package setup script |
| 18 | `tools/flowcore/requirements.txt` | Text | ~0.1KB | Python dependencies |
| 19 | `tools/flowcore/config/config.yaml` | YAML | ~0.9KB | Framework configuration (browser, proxy, registrar) |
| 20 | `tools/flowcore/scripts/run_pipeline.py` | Python | ~0.3KB | Pipeline runner entry point |
| 21 | `tools/flowcore/scripts/refresh_proxies.py` | Python | ~0.6KB | Proxy pool refresh script |
| 22 | `tools/flowcore/tests/test_browser.py` | Python | ~0.9KB | Test suite for FlowCore modules |
| 23 | `tools/flowcore/docs/TUTORIAL.md` | Markdown | ~8.3KB | Complete usage tutorial |
| 24 | `tools/flowcore/flowcore/__init__.py` | Python | 0B | Package init (empty) |
| 25 | `tools/flowcore/flowcore/core/__init__.py` | Python | 0B | Core package init (empty) |
| 26 | `tools/flowcore/flowcore/core/browser.py` | Python | ~5.2KB | Playwright wrapper with stealth, fingerprint, proxy |
| 27 | `tools/flowcore/flowcore/core/fingerprint.py` | Python | ~1.9KB | Identity profile generator |
| 28 | `tools/flowcore/flowcore/modules/__init__.py` | Python | 0B | Modules init (empty) |
| 29 | `tools/flowcore/flowcore/modules/registrar.py` | Python | ~7.4KB | Form automation engine (Discord, Fiverr, Reddit) |
| 30 | `tools/flowcore/flowcore/modules/scraper.py` | Python | ~1.6KB | Anti-detection web scraper |
| 31 | `tools/flowcore/flowcore/modules/watcher.py` | Python | ~3.8KB | Pipeline monitoring & opportunity tracking |
| 32 | `tools/flowcore/flowcore/utils/__init__.py` | Python | 0B | Utils init (empty) |
| 33 | `tools/flowcore/flowcore/utils/names.py` | Python | ~2KB | Identity generator (names, emails, passwords) |
| 34 | `tools/flowcore/flowcore/utils/network.py` | Python | ~3.2KB | Proxy pool manager with health checks |

## 🛠️ STANDALONE TOOLS (6 files)

| # | Path | Type | Size | Description |
|---|------|------|------|-------------|
| 35 | `tools/ghost_creator.py` | Python | ~14KB | **🔥 GHOST v1.0** — Mass account creator (Fiverr, Reddit, Discord) |
| 36 | `tools/ghost_tester.py` | Python | ~6.8KB | **🔥 Turnstile Bypass Tester** — Tests Cloudflare bypass capability |
| 37 | `tools/income_pipeline.py` | Python | ~7KB | **💰 Income Pipeline** — Money opportunity scraper (duplicate of #6) |
| 38 | `tools/farming_guide.py` | Python | ~5.4KB | **🌐 Testnet/airdrop guide** — Faucets, platforms, earnings estimation |
| 39 | `tools/airdrop_monitor.py` | Python | ~4.6KB | **📡 Airdrop monitor** — Checks Galxe, Layer3, faucets, Reddit |
| 40 | `tools/README.md` | Markdown | ~2.9KB | Tools directory documentation |

## 📊 DATA FILES (1 file)

| # | Path | Type | Size | Description |
|---|------|------|------|-------------|
| 41 | `data/subdomains_raw.txt` | Text | ~39KB | **Bug bounty subdomain enumeration** — Tokopedia & Bukalapak targets |

## 📜 ROOT DOCUMENTS (3 files)

| # | Path | Type | Size | Description |
|---|------|------|------|-------------|
| 42 | `setup.sh` | Shell | ~10.6KB | **Full restore script** — Installs everything automatically |
| 43 | `README.md` | Markdown | ~5.9KB | Repository documentation and restore guide |
| 44 | `INVENTORY.md` | Markdown | ~5KB | This file — complete file manifest |

## 📦 FILE STATISTICS

| Category | File Count | Total Size (approx) |
|----------|-----------|-------------------|
| Python scripts | 17 | ~91 KB |
| YAML config | 3 | ~18 KB |
| Shell scripts | 2 | ~11 KB |
| JSON data | 1 | ~6 KB |
| SQLite DB | 1 | varies |
| SSH keys | 2 | ~0.5 KB |
| Markdown docs | 5 | ~25 KB |
| Text data | 2 | ~40 KB |
| Text/LICENSE | 1 | ~1 KB |
| Package init | 5 | 0 B (empty) |
| **Total** | **44** | **~192 KB + state.db** |

## 🔄 CRON SCHEDULE SUMMARY

| Job Name | Script | Schedule | Deliver To |
|----------|--------|----------|------------|
| 🚨 FBI Watchdog | `monitor.py` | Every 360m | Telegram |
| 📊 FBI Daily Briefing | `daily_report.py` | 0 16 * * * (daily 16:00 UTC) | Telegram |
| 🧹 Hermes Session Prune | `prune.sh` | 0 3 * * 1 (weekly Monday) | Local |
| 💰 Income Pipeline | `income_pipeline.py` | Every 360m | Origin (Telegram) |
| 🔁 Proxy Auto-Updater | `proxy_updater.py` | Every 360m | Local |
