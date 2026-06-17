# 📖 FlowCore VPS — Complete Usage Guide

> *Backup VPS grace-ku-sayang — restore, monitor, dan manage kayak pro.*
> Bahasa Indonesia campur Inggris dikit. Ramah untuk non-coder.

---

## 📑 Daftar Isi

- [Cara Install](#-cara-install)
- [Struktur Folder](#-struktur-folder)
- [12 Cron Jobs](#-12-cron-jobs)
- [Tools & Dependencies](#-tools--dependencies)
- [Verification Checklist](#-verification-checklist)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Cara Install

### Step-by-step dari VPS baru

```bash
# 1. Clone repo
git clone https://github.com/leonidastcejorp/flowcore-vps.git
cd flowcore-vps

# 2. Cek kondisi VPS — HARUS jalanin ini dulu!
bash pre-flight.sh
```

**Output pre-flight.sh:**
```json
{"os": {"version": "24.04", "codename": "noble"},
 "apt_locked": false,
 "bg_updates": false,
 "ram_mb": 1800,
 "disk_mb": 35000,
 "internet": true,
 "status": "ready"}
```

Kalo status **"blocked"**, jangan lanjut — cek Troubleshooting bagian A dulu.

```bash
# 3. Kalo status "ready", jalanin setup
bash setup.sh
# ~10-15 menit, no interaction needed
```

**Yang diinstall setup.sh:**

| Step | Apa | Waktu |
|------|-----|-------|
| 1 | System packages (git, curl, python3, build-essential) | ~2 menit |
| 2 | Python venv + Hermes Agent v0.16.0 | ~1 menit |
| 3 | Hermes config, SOUL.md, plugins | 5 detik |
| 4 | SSH keys | 2 detik |
| 5 | Go tools (nuclei, subfinder, httpx) — atau fallback binary | ~3 menit |
| 6 | Playwright + Chromium | ~2 menit |
| 7 | FlowCore toolkit | 5 detik |
| 8 | Security tools (fail2ban, lynis, rkhunter, clamav) | ~3 menit |
| 9 | System tweaks (swappiness, DNS, journal limits) | 10 detik |
| 10 | **Reboot prompt** | — |

```bash
# 4. Setup selesai — isi API key
# Edit ~/.hermes/config.yaml atau ~/.hermes/.env
# Yang WAJIB: model.api_key (provider LLM)
# Optional: Telegram bot token, TTS keys, dll.

# 5. Deploy 12 cron jobs
bash deploy-cron.sh

# 6. Reboot
sudo reboot
```

### Support Ubuntu 22.04 & 24.04

| OS | Kernel | Catatan |
|----|--------|---------|
| **Ubuntu 22.04 LTS** | 5.15+ | Tested fully. Package names: `python3-pip`, `chromium-browser` |
| **Ubuntu 24.04 LTS** | 6.8+ | Tested. Package names beda dikit — setup.sh auto-detect. `python3-pip` → `python3-pip` (sama) |

Bedanya: Ubuntu 24.04 punya package names lebih baru untuk beberapa tool (e.g., `chromium` instead of `chromium-browser`). Setup.sh otomatis detek dari `/etc/os-release` dan pilih package names yang cocok.

---

## 📁 Struktur Folder

```
flowcore-vps/
├── README.md                   # This file — quick start
├── INVENTORY.md                # Complete file manifest
├── TUTORIAL.md                 # This file — usage guide
├── setup.sh                    # Main setup script
├── pre-flight.sh               # Pre-flight check (jalanin SEBELUM setup)
├── deploy-cron.sh              # Deploy 12 cron jobs
├── CONFIG_REFERENCE.md         # Config.yaml reference lengkap
├── SUMMARY.md                  # Tools & dependencies reference
│
├── hermes/                     # Hermes Agent
│   ├── config.yaml             #   Main config (API keys redacted)
│   ├── SOUL.md                 #   BREACH v3.0 personality
│   ├── SOUL.backup.md          #   Default personality backup
│   ├── state.db                #   State database (5.4 MB)
│   ├── scripts/                #   ⭐ 15 scripts
│   │   ├── monitor.py          #     🚨 FBI Watchdog
│   │   ├── daily_report.py     #     📊 Daily Briefing
│   │   ├── income_pipeline.py  #     💰 CuanFeed
│   │   ├── proxy_updater.py    #     🔁 Proxy Pool
│   │   ├── prune.sh            #     🧹 Session Prune
│   │   ├── context_monitor.py  #     📈 LogDesk
│   │   ├── disk_alert.sh       #     💾 DiskBay
│   │   ├── error_summary.py    #     📋 Briefing
│   │   ├── memory_monitor.py   #     📈 MemStat
│   │   ├── ssh_attack_monitor.py #   🚪 PortGuard
│   │   ├── reboot_monitor.py   #     🔁 Bootmark
│   │   ├── vps_backup.sh       #     📦 Backup
│   │   └── lib/                #     Library
│   │       ├── error_log.py    #       Error logging (Python)
│   │       └── error_log.sh    #       Error logging (Shell)
│   ├── plugins/rtk-rewrite/    #   RTK command rewrite plugin
│   │   ├── __init__.py
│   │   └── plugin.yaml
│   └── cron/jobs.json          #   Cron job definitions (5→12 jobs)
│
├── ssh/                        # SSH keys
│   ├── id_ed25519              #   🔴 PRIVATE KEY
│   └── id_ed25519.pub          #   Public key
│
├── tools/                      # Standalone tools & frameworks
│   ├── flowcore/               #   Full FlowCore toolkit (20 files)
│   ├── ghost_creator.py        #   🔥 Mass account creator
│   ├── ghost_tester.py         #   🔥 Turnstile bypass tester
│   ├── income_pipeline.py      #   💰 Income scraper
│   ├── farming_guide.py        #   🌐 Airdrop guide
│   ├── airdrop_monitor.py      #   📡 Airdrop monitor
│   └── README.md               #   Tools documentation
│
└── data/
    └── subdomains_raw.txt      #   Bug bounty subdomains
```

---

## ⏰ 12 Cron Jobs

Semua scripts pake **NO-AGENT mode** — gak pake LLM, langsung execute. Hemat token.

| # | Nama Job | Nickname | Script | Schedule | Deliver |
|---|----------|----------|--------|----------|---------|
| 1 | 🚨 FBI Watchdog | — | `monitor.py` | every 360m | Telegram |
| 2 | 📊 FBI Daily Briefing | — | `daily_report.py` | 0 16 * * * | Telegram |
| 3 | 🧹 Hermes Session Prune | — | `prune.sh` | 0 3 * * 1 | Local |
| 4 | 💰 Income Pipeline | CuanFeed | `income_pipeline.py` | every 360m | Telegram |
| 5 | 🔁 Proxy Auto-Updater | — | `proxy_updater.py` | every 360m | Local |
| 6 | 📦 VPS Weekly Backup | Backup | `vps_backup.sh` | 0 2 * * 0 | Local |
| 7 | 💾 Disk Usage Watchdog | DiskBay | `disk_alert.sh` | every 360m | Telegram |
| 8 | 📈 Context Monitor | LogDesk | `context_monitor.py` | every 60m | Telegram |
| 9 | 🚪 SSH Attack Monitor | PortGuard | `ssh_attack_monitor.py` | every 360m | Telegram |
| 10 | 🔁 Reboot Monitor | Bootmark | `reboot_monitor.py` | every 15m | Telegram |
| 11 | 📈 Memory Pressure | MemStat | `memory_monitor.py` | every 60m | Telegram |
| 12 | 📋 Error Log Summary | Briefing | `error_summary.py` | every 360m | Telegram |

**Delivery details:**
- **Telegram group** (8 jobs): Kantor FBI `-1003534226714`
- **Local** (3 jobs): Hasil cuma disimpan lokal, gak dikirim kemana-mana
- **Briefing** (1 job): Error summary, dikirim ke Telegram

### Deploy cron jobs

```bash
# Sekali jalan — idempotent, aman dijalanin ulang
bash deploy-cron.sh

# Manual: check status
hermes cron list
hermes cron run <job-id>
```

### Cron schedule reference

| Schedule | Arti |
|----------|------|
| `every 15m` | Tiap 15 menit |
| `every 60m` | Tiap 1 jam |
| `every 360m` | Tiap 6 jam |
| `0 16 * * *` | Setiap hari jam 16:00 UTC |
| `0 3 * * 1` | Setiap Senin jam 03:00 UTC |
| `0 2 * * 0` | Setiap Minggu jam 02:00 UTC |

---

## 🛠️ Tools & Dependencies

### System Tools

| Tool | Version | Install |
|------|---------|---------|
| Hermes Agent | v0.16.0 | `curl -fsSL https://hermes-agent.nousresearch.com/install.sh \| bash` |
| Python 3 | ≥ 3.10 | `apt install python3 python3-pip python3-venv` |
| Go | ≥ 1.21 | `wget https://go.dev/dl/go1.22.2.linux-amd64.tar.gz && tar -C /usr/local -xzf go*.tar.gz` |
| Node.js | ≥ 20 LTS | Via NVM: `nvm install --lts` |
| Playwright | ≥ 1.40 | `pip install playwright && playwright install chromium` |
| Chromium | ≥ 120 | `apt install chromium-browser` |
| fail2ban | ≥ 0.11 | `apt install fail2ban` |
| lynis | ≥ 3.0 | `apt install lynis` |
| rkhunter | ≥ 1.4 | `apt install rkhunter` |
| ClamAV | ≥ 0.103 | `apt install clamav clamav-daemon` |

### Security Tools (Go-based)

| Tool | Install |
|------|---------|
| nuclei | `go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest` |
| subfinder | `go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest` |
| httpx | `go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest` |

**Fallback:** Kalo `go install` gagal, setup.sh otomatis download pre-built binary dari GitHub releases.

### Python Packages

| Package | Guna |
|---------|------|
| `playwright` | Browser automation |
| `requests` / `httpx` | HTTP calls |
| `psutil` | System monitoring |
| `python-dotenv` | .env loading |
| `rich` | Pretty CLI output |

---

## ✅ Verification Checklist

Jalanin ini abis setup buat verifikasi semuanya oke:

- [ ] **Git clone** — `git status` shows clean working tree
- [ ] **Hermes** — `hermes status` atau `hermes --version` → v0.16.0
- [ ] **Cron** — `hermes cron list` shows 12 jobs
- [ ] **API Keys** — Terisi di `~/.hermes/config.yaml` atau `.env`
- [ ] **Monitor** — `python3 ~/.hermes/scripts/monitor.py` runs without error
- [ ] **Playwright** — `playwright install --with-deps chromium`
- [ ] **Nuclei** — `nuclei -version` ≥ 3.x
- [ ] **Subfinder** — `subfinder -version`
- [ ] **HTTPx** — `httpx -version`
- [ ] **fail2ban** — `sudo fail2ban-client status`
- [ ] **SSH Key** — `chmod 600 ~/.ssh/id_ed25519`
- [ ] **Disk** — `df -h` shows reasonable usage
- [ ] **Telegram** — Cek grup Kantor FBI, ada notifikasi masuk

---

## 🐛 Troubleshooting

### A. ERROR GIT CLONE — Background update blocking

**Masalah:** Waktu `git clone`, keluar error kayak "Could not lock file" atau "waiting for apt". Biasanya gara-gara VPS lagi jalanin background update (unattended-upgrades).

**Solusi #1 (paling gampang):** Jalanin `bash pre-flight.sh` dulu. Dia bakal detek kalo ada proses apt berjalan.

**Solusi #2 (manual):**
```bash
ps aux | grep apt
# Kalo ada proses apt, tunggu sampe selesai (5-15 menit)
```

**Solusi #3 (force stop kalo macet):**
```bash
sudo killall apt-get
sudo killall dpkg
# Then cleanup:
sudo rm -f /var/lib/dpkg/lock-frontend
sudo rm -f /var/lib/apt/lists/lock
sudo rm -f /var/cache/apt/archives/lock
sudo dpkg --configure -a
```

### B. ERROR "sys not defined" — income_pipeline.py

**Masalah:** Script `income_pipeline.py` pake `sys.path.insert(...)` tapi lupa `import sys`. Error:
```
NameError: name 'sys' is not defined
```

**Solusi:** Udah di-fix di repo. Kalo masih muncul di cron, update script:
```bash
# Fix: tambahin "import sys" di baris 1
sed -i '1iimport sys' ~/.hermes/scripts/income_pipeline.py
```

Atau re-deploy cron job:
```bash
hermes cron remove <job-id-pipeline>
bash deploy-cron.sh  # auto-skip yg udah ada
```

### C. OS Version Error — Ubuntu 22 vs 24

**Masalah:** Ubuntu 22.04 dan 24.04 punya package names beda. Contoh: `chromium-browser` di 22.04 jadi `chromium` di 24.04.

**Solusi:** Udah di-fix. `setup.sh` otomatis detek OS version dari `/etc/os-release` dan pilih package names yang cocok. Gak perlu manual.

Kalo penasaran, liat di setup.sh bagian:
```bash
if [[ "$OS_VERSION" == "24.04" ]]; then
    PKG_CHROMIUM="chromium"
else
    PKG_CHROMIUM="chromium-browser"
fi
```

### D. Hermes Gak Keinstall

**Masalah:** setup.sh gagal install Hermes Agent, biasanya karena network issue atau curl error.

**Solusi — install manual:**
```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

**Atau kalo mau specific version:**
```bash
pip install hermes-agent==0.16.0
```

**Verify:**
```bash
hermes --version
# → hermes version 0.16.0
```

### E. Go Tools Error — Install Gagal

**Masalah:** `go install` buat nuclei/subfinder/httpx gagal — biasanya karena Go version terlalu tua, network blocked, atau memory kurang.

**Solusi:** setup.sh otomatis fallback ke pre-built binary dari GitHub releases:
- nuclei: `github.com/projectdiscovery/nuclei/releases`
- subfinder: `github.com/projectdiscovery/subfinder/releases`
- httpx: `github.com/projectdiscovery/httpx/releases`

**Manual:**
```bash
# Contoh download nuclei binary langsung
wget https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_3.x.x_linux_amd64.zip
unzip nuclei_*.zip
sudo mv nuclei /usr/local/bin/
```

### F. Deploy-cron Gagal — Hermes Belum Running

**Masalah:** `bash deploy-cron.sh` error: "Hermes CLI not found".

**Solusi:** Install Hermes dulu:
```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
# or
pip install hermes-agent
```

### G. Telegram Bot Gak Kirim Notifikasi

**Masalah:** Cron jobs jalan tapi gak ada notifikasi di Telegram.

**Cek:**
```bash
# 1. Apakah Telegram bot token sudah diisi?
grep -i telegram ~/.hermes/config.yaml

# 2. Cek cron job status
hermes cron list | grep -i telegram

# 3. Cek log
journalctl -u hermes --since "1 hour ago" --no-pager | grep -i deliver
```

**Solusi:** Pastiin Telegram bot token udah diisi di `~/.hermes/.env`:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### H. VPS Lemot Abis Install

**Masalah:** Abis jalanin setup.sh, VPS terasa lambat.

**Penyebab:** ClamAV lagi scan, atau background processes.
```bash
# Cek beban
htop
# atau
top

# Pause ClamAV kalo perlu
sudo systemctl stop clamav-daemon

# Cek swap usage
free -h
```

### I. Cron Jobs Gak Jalan (Hermes Cron Issue)

**Masalah:** `hermes cron list` nunjukin jobs tapi gak ada yang execute.

```bash
# 1. Cek hermes daemon jalan
systemctl status hermes

# 2. Restart kalo perlu
sudo systemctl restart hermes

# 3. Cek cron scheduler
hermes cron list --verbose

# 4. Test manual satu job
hermes cron run <job-id>
```

---

## 💡 Tips

| Tip | Detail |
|-----|--------|
| **Simpan token** | Semua cron NO-AGENT — gak pake LLM, hampir gratis |
| **Monitor Telegram** | Join grup Kantor FBI untuk alert real-time |
| **Backup rutin** | Cron job #6 (VPS Weekly Backup) jalan tiap Minggu |
| **SSH monitoring** | PortGuard (#9) lapor kalo ada brute-force attempt |
| **Disk alert** | DiskBay (#7) silent kalo aman, baru notif kalo >80% |
| **Bootmark** | (#10) tiap 15 menit detek kalo VPS restart mendadak |
| **Multiple profiles** | `hermes --profile <nama>` untuk personality beda |

---

*Hermes Agent v0.16.0 · Model: deepseek/deepseek-v4-flash · FlowCore VPS Backup*
