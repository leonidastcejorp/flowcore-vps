# 📖 FlowCore VPS — Complete Usage Guide

> *Your portable AI agent environment — backup, restore, and manage like a pro.*

---

## 📑 Table of Contents

- [🚀 Quick Restore](#-quick-restore)
- [📁 Understanding the Structure](#-understanding-the-structure)
- [🤖 Hermes Agent CLI](#-hermes-agent-cli)
- [⏰ Cron Job Management](#-cron-job-management)
- [📡 Server Watchdog (Monitor)](#-server-watchdog-monitor)
- [💰 Income Pipeline](#-income-pipeline)
- [👻 Ghost Framework (Account Creator)](#-ghost-framework-account-creator)
- [🌐 Proxy Management](#-proxy-management)
- [🔧 Tool Reference](#-tool-reference)
- [🐛 Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Restore

### On a Fresh VPS (Ubuntu 22.04+)

```bash
# 1. Clone
git clone https://github.com/leonidastcejorp/flowcore-vps.git
cd flowcore-vps

# 2. Run automatic restore (installs EVERYTHING)
chmod +x setup.sh
sudo ./setup.sh

# 3. Update API keys
nano ~/.hermes/config.yaml
# → Replace YOUR_*_HERE with your real keys

# 4. Verify everything
hermes status

# 5. Reboot (recommended)
sudo reboot
```

### What setup.sh Does Automatically

| Step | What | Time |
|------|------|------|
| 1 | System packages (git, curl, python3, build-essential, etc.) | ~2 min |
| 2 | Python venv + Hermes Agent install | ~1 min |
| 3 | Hermes config, SOUL.md, plugins | 5 sec |
| 4 | SSH keys restore | 2 sec |
| 5 | Go tools (nuclei, subfinder, httpx) | ~3 min |
| 6 | Playwright + Chromium | ~2 min |
| 7 | FlowCore toolkit as editable package | 5 sec |
| 8 | WireGuard (optional, skips if no .conf) | 2 sec |
| 9 | Cron jobs + systemd journal limits | 10 sec |
| 10 | Reboot prompt | — |

**Total: ~10 minutes, zero interaction needed.**

---

## 📁 Understanding the Structure

```
~/.hermes/                    # Hermes Agent home
├── config.yaml               # 🔑 API keys, model, provider settings
├── SOUL.md                   # Agent personality (BREACH v3.0)
├── state.db                  # Session database
├── profiles/default/         # Active profile
├── scripts/                  # Cron & utility scripts
│   ├── monitor.py            # 📡 System watchdog
│   ├── income_pipeline.py    # 💰 Income scraper
│   ├── proxy_updater.py      # 🔄 Proxy refresh
│   ├── daily_report.py       # 📊 Daily briefing
│   └── prune.sh              # 🧹 Session cleanup
├── plugins/rtk-rewrite/      # RTK token-saving plugin
└── cron/jobs.json            # Scheduled jobs
```

---

## 🤖 Hermes Agent CLI

### Basic Commands

```bash
# Check status
hermes status

# Start/Stop
hermes start
hermes stop

# Run a one-off task
hermes run "scan 10 subdomains of example.com"

# View logs
journalctl -u hermes -n 50 --no-pager
```

### Configuration

```bash
# Edit config
hermes config edit

# Set model
hermes config set model "deepseek/deepseek-v4-flash"

# Set provider
hermes config set provider "openrouter"

# List tools
hermes tools
```

---

## ⏰ Cron Job Management

### Active Jobs (from backup)

| Job | Schedule | Description |
|-----|----------|-------------|
| 📡 Surveillance Report | Every 6h | Server health + token usage |
| 🧹 Session Prune | Monday 3am | Cleans old sessions >30 days |
| 💰 Income Pipeline | Every 6h | Scrapes freelance + airdrops |

### Manage with Hermes

```bash
# List all jobs
hermes cron list

# Run a job immediately
hermes cron run <job-id>

# Pause/Resume
hermes cron pause <job-id>
hermes cron resume <job-id>

# Remove
hermes cron remove <job-id>
```

### Manual Crontab

```bash
# Edit system crontab
crontab -e

# View current cron jobs
crontab -l
```

---

## 📡 Server Watchdog (Monitor)

The monitor script runs every 6 hours and sends alerts to your Telegram.

### What It Checks

| Metric | 🟢 Healthy | 🟡 Warning | 🔴 Critical | 💀 Danger |
|--------|------------|------------|-------------|-----------|
| **RAM** | < 70% | 70-82% | 82-92% | > 92% |
| **Disk** | < 78% | 78-88% | 88-93% | > 93% |
| **CPU Load** | < 1.4 | 1.4-2.0 | 2.0-3.0 | > 3.0 |

### Run Manually

```bash
cd /root/flowcore-vps
python3 -m hermes.scripts.monitor
```

### What It Reports

- ✅ Hardware health (RAM, CPU, Disk, uptime)
- 📊 Token usage from Hermes state.db
- 💰 RTK token savings (if plugin active)
- 🔄 Daily backup status
- ⚠️ Recent errors from journald
- 🎯 Recommendations if thresholds exceeded

---

## 💰 Income Pipeline

### What It Does

Scrapes **freelance gigs + airdrop opportunities** every 6 hours and delivers them to your Telegram.

### Available Sources

| Source | Type | Status |
|--------|------|--------|
| Upwork | Freelance | 🟢 Active |
| Freelancer | Freelance | 🟢 Active |
| PeoplePerHour | Freelance | 🟢 Active |
| Testnet Faucets | Airdrop | 🟢 Active |
| DropsTab | Airdrop | 🟢 Active |
| QuestN | Airdrop | 🟢 Active |

### Run Manually

```bash
cd /root/flowcore-vps
python3 -m hermes.scripts.income_pipeline
```

### Change Frequency

```bash
# Edit cron schedule
hermes cron update <pipeline-job-id> --schedule "every 3h"
```

### Farming Guide

```bash
# View airdrop farming strategies
cd /root/flowcore-vps/tools
python3 farming_guide.py --help
```

---

## 👻 Ghost Framework (Account Creator)

### Mass Account Creator

```bash
cd /root/flowcore-vps/tools

# Discord accounts (works from VPS!)
python3 ghost_creator.py --platform discord --count 10 --output accounts.json

# Fiverr/Reddit (needs clean proxy)
python3 ghost_creator.py --platform fiverr --proxy socks5://user:pass@ip:port

# Test Turnstile bypass
python3 ghost_tester.py --url "https://example.com/login" --headless
```

### Limitations

| Platform | From VPS | From Home IP | Notes |
|----------|----------|--------------|-------|
| Discord | ✅ Works | ✅ | No captcha |
| Fiverr | ❌ Blocked | ✅ Works | Needs Turnstile bypass |
| Reddit | ❌ Blocked | ⚠️ Tricky | Needs phone verify |
| Gmail | ❌ Blocked | ⚠️ Tricky | SMS verification |

> **Tip**: Save accounts to `data/` directory for organized storage:
> ```bash
> python3 ghost_creator.py --platform discord --output data/discord_accounts_$(date +%Y%m%d).json
> ```

---

## 🌐 Proxy Management

### Auto-Updater

```bash
# Run once
python3 proxy_updater.py

# Check current proxy pool
ls -la ~/.flowcore/proxies/
cat ~/.flowcore/proxies/http.txt | wc -l
```

### Proxy Sources

The tool automatically fetches from 4 public proxy lists:
- `databay-labs` (HTTP + SOCKS5)
- `r00tee` (HTTPS + SOCKS5)
- **~17,000 proxies** checked → typically ~5-50 alive

### Testing Proxies

```bash
# Test a specific proxy
curl -x http://1.2.3.4:8080 -s -o /dev/null -w "%{http_code}" https://api.ipify.org

# Test multiple
while read proxy; do
  if curl -x "http://$proxy" -s -m 5 -o /dev/null -w "%{http_code}" https://api.ipify.org | grep -q 200; then
    echo "$proxy ✅"
  fi
done < ~/.flowcore/proxies/http.txt
```

---

## 🔧 Tool Reference

### FlowCore Framework

```bash
cd /root/flowcore-vps/tools/flowcore

# Browser automation
python3 -m flowcore.core.browser --url "https://example.com"

# Web scraper
python3 -m flowcore.modules.scraper --url "https://target.com" --output data/scraped.json

# Form automation (registrar)
python3 -m flowcore.modules.registrar --platform discord

# Monitor dashboard
python3 -m flowcore.modules.watcher --daemon

# Refresh proxies
python3 -m flowcore.utils.network --refresh --test

# Generate identity
python3 -m flowcore.utils.names --count 10 --format json
```

### Security Tools

```bash
# Subdomain enumeration
subfinder -d example.com -all -o /tmp/subs.txt

# Web probing
httpx -l /tmp/subs.txt -status-code -title -tech-detect

# Vulnerability scanning
nuclei -l /tmp/subs.txt -severity critical,high -o /tmp/critical.txt

# Full pipeline (one-liner)
subfinder -d example.com -silent | httpx -silent | nuclei -severity critical,high
```

### Ghost Tools

```bash
cd /root/flowcore-vps/tools

python3 ghost_creator.py --help      # Account creator
python3 ghost_tester.py --help       # Bypass tester
python3 airdrop_monitor.py --help    # Airdrop monitoring
python3 farming_guide.py             # Airdrop strategies
```

### Monitoring

```bash
cd /root/flowcore-vps/tools

python3 income_pipeline.py           # Run income pipeline
python3 proxy_updater.py             # Refresh proxies
python3 daily_report.py              # Manual daily report
```

---

## 🐛 Troubleshooting

### Hermes Won't Start

```bash
# Check config syntax
hermes config validate

# Check logs
journalctl -u hermes --since "5 minutes ago" --no-pager

# Common fix: reinstall
pip install --upgrade hermes-agent

# Reset config
hermes config init
```

### Playwright Fails

```bash
# Reinstall Chromium
playwright install --with-deps chromium

# Check deps
ldd $(which chromium) | grep "not found"

# Force reinstall
playwright uninstall chromium
playwright install chromium
```

### Git Push Fails

```bash
# Check SSH key
ssh -T git@github.com
# Expected: "Hi leonidastcejorp! You've successfully authenticated"

# Re-add SSH key
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub  # → Add to GitHub Settings → SSH Keys

# Test again
ssh -T git@github.com
```

### Go Tools Not Installed

```bash
# Install manually
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# Restart shell
exec $SHELL
```

### Cron Jobs Not Running

```bash
# Check cron status
systemctl status cron

# Check crontab
crontab -l

# Enable cron
sudo systemctl enable --now cron

# Check cron logs
grep -i "hermes\|pipeline\|monitor\|airdrop" /var/log/syslog | tail -20
```

### "IP Blocked" / 403 Errors

```bash
# Check current IP
curl -s https://api.ipify.org

# Use proxy with tool
python3 ghost_creator.py --platform fiverr --proxy socks5://proxy:1080

# Or use a different approach: run from home IP / home server
```

### Out of Disk Space

```bash
# Check usage
df -h

# Clean journal logs
sudo journalctl --vacuum-time=3d

# Clean pip cache
pip cache purge

# Remove old sessions
find ~/.hermes/sessions/ -mtime +30 -delete

# Remove apt cache
sudo apt clean
```

---

## 🔐 Post-Restore Checklist

- [ ] **API Keys** — Updated in `~/.hermes/config.yaml`
- [ ] **SSH Key** — `chmod 600 ~/.ssh/id_ed25519`
- [ ] **Hermes** — `hermes status` shows "running"
- [ ] **Playwright** — `playwright install --with-deps chromium`
- [ ] **Go Tools** — `nuclei -version` ≥ 3.x
- [ ] **Cron** — `hermes cron list` shows all 3 jobs
- [ ] **Monitor** — Runs without errors: `python3 -m hermes.scripts.monitor`
- [ ] **Backup** — `git status` shows clean working tree

---

## 💡 Pro Tips

| Tip | Details |
|-----|---------|
| **Save tokens** | RTK plugin auto-rewrites commands — saves 60-90% tokens |
| **Keep backup fresh** | Run `./setup.sh --backup-only` weekly |
| **Monitor alerts** | Go to Telegram → Kantor FBI → Surveillance topic |
| **Multiple profiles** | `hermes config set profile work` to switch agent personalities |
| **Auto-recovery** | Cron monitor auto-restarts Hermes if it crashes |
| **Session search** | `hermes session search "keywords"` finds past conversations |

---

*Generated with Hermes Agent · Part of the FlowCore Ecosystem*
