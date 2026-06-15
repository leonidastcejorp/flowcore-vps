# FlowCore VPS Backup Repository 🔄

> **Complete backup of a production VPS environment**
> Ubuntu 22.04 · 2c/2GB/40GB · Kernel 5.15.0-181-generic

## 📋 Overview

This repository contains a complete snapshot of the FlowCore VPS environment, including:

- **Hermes Agent** configuration, personality, scripts, plugins, and cron jobs
- **SSH keys** (public + encrypted private key)
- **FlowCore Toolkit** — Full enterprise workflow automation framework
- **Ghost Framework** — Mass account creation tools (Fiverr, Reddit, Discord)
- **Income Pipeline** — Automated money opportunity scraper & analyzer
- **Proxy Management** — Auto-updating proxy pool from public sources
- **Subdomain Data** — Bug bounty reconnaissance output
- **Monitoring Suite** — Server watchdog, daily briefings, session pruning

## 🚀 How to Restore

```bash
# 1. Clone this repo on your new Ubuntu 22.04 VPS
git clone https://github.com/leonidastcejorp/flowcore-vps.git
cd flowcore-vps

# 2. Run the full restore script
chmod +x setup.sh
sudo ./setup.sh

# 3. Update API keys in ~/.hermes/config.yaml
#    Edit the file and replace YOUR_API_KEY_HERE with your real keys

# 4. Reboot (recommended)
sudo reboot
```

## 📁 Repository Structure

```
flowcore-vps/
├── setup.sh                          # Automatic restore script
├── README.md                         # This file
├── INVENTORY.md                      # Complete file manifest
│
├── hermes/                           # Hermes Agent configuration
│   ├── config.yaml                   #   Main config (API keys redacted)
│   ├── SOUL.md                       #   Agent personality (BREACH v3.0)
│   ├── SOUL.backup.md                #   Default personality backup
│   ├── state.db                      #   Hermes state database
│   ├── scripts/                      #   Cron scripts
│   │   ├── monitor.py                #     📡 FBI Watchdog (server monitor)
│   │   ├── income_pipeline.py        #     💰 Income opportunity scraper
│   │   ├── proxy_updater.py          #     🔄 Proxy auto-updater
│   │   ├── daily_report.py           #     📊 Daily briefing generator
│   │   └── prune.sh                  #     🧹 Session pruner
│   ├── plugins/rtk-rewrite/          #   RTK command rewrite plugin
│   │   ├── __init__.py
│   │   └── plugin.yaml
│   └── cron/jobs.json                #   Scheduled cron job definitions
│
├── ssh/                              # SSH keys
│   ├── id_ed25519                    #   🔴 PRIVATE KEY (sensitive!)
│   └── id_ed25519.pub                #   Public key
│
├── tools/                            # Standalone tools
│   ├── flowcore/                     #   Full FlowCore framework
│   │   ├── README.md                 #     Framework documentation
│   │   ├── LICENSE                   #     MIT License
│   │   ├── setup.py                  #     Python package setup
│   │   ├── requirements.txt          #     Dependencies
│   │   ├── config/config.yaml        #     Framework config
│   │   ├── scripts/                  #     Utility scripts
│   │   │   ├── run_pipeline.py
│   │   │   └── refresh_proxies.py
│   │   ├── tests/test_browser.py     #     Test suite
│   │   ├── docs/TUTORIAL.md          #     Complete tutorial
│   │   └── flowcore/                 #     Python package
│   │       ├── core/
│   │       │   ├── browser.py        #       Playwright wrapper
│   │       │   └── fingerprint.py    #       Fingerprint engine
│   │       ├── modules/
│   │       │   ├── registrar.py      #       Form automation
│   │       │   ├── scraper.py        #       Data collection
│   │       │   └── watcher.py        #       Pipeline monitoring
│   │       └── utils/
│   │           ├── names.py          #       Identity generator
│   │           └── network.py        #       Proxy manager
│   ├── ghost_creator.py              #   🔥 Mass account creator
│   ├── ghost_tester.py               #   🔥 Turnstile bypass tester
│   ├── income_pipeline.py            #   💰 Money opportunity scraper
│   ├── farming_guide.py              #   🌐 Testnet/airdrop guide
│   └── airdrop_monitor.py            #   📡 Airdrop campaign monitor
│
└── data/                             # Data files
    └── subdomains_raw.txt            #   Bug bounty subdomain list
```

## ⚙️ VPS Specifications

| Spec | Value |
|------|-------|
| OS | Ubuntu 22.04 LTS |
| Kernel | 5.15.0-181-generic |
| CPU | 2 cores |
| RAM | 2 GB |
| Disk | 40 GB |
| Swappiness | 10 |
| DNS | Cloudflare 1.1.1.1 / Google 8.8.8.8 |

## 🔑 Post-Restore Checklist

1. **API Keys** — Update `YOUR_API_KEY_HERE` in `~/.hermes/config.yaml`
2. **SSH Keys** — The private key is marked as sensitive; validate permissions (`chmod 600 ~/.ssh/id_ed25519`)
3. **Hermes** — Start Hermes: `hermes start` or `systemctl start hermes`
4. **Cron** — Verify cron jobs: `hermes cron list`
5. **Playwright** — Verify Chromium: `playwright install --with-deps chromium`
6. **Go Tools** — Check nuclei/subfinder/httpx: `nuclei -version`

## 🛡️ Security Notes

- API keys have been **redacted** in `config.yaml` — replace with real keys before using
- SSH private key is included but should be **regenerated** for production use
- The BREACH v3.0 SOUL.md is an **unrestricted agent personality** — use with caution

---

*Built with Hermes Agent · Backup generated 2026-06-15*
