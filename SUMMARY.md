# SUMMARY.md — Tools & Dependencies Reference

> Daftar lengkap semua tools yang digunakan di Flowcore VPS, termasuk versi, metode install, dan link download.

---

## System Tools

| Tool | Version | Install Method | Link |
|------|---------|---------------|------|
| Git | ≥ 2.30 | `apt install git` | https://git-scm.com/downloads |
| curl | ≥ 7.68 | `apt install curl` | https://curl.se/download.html |
| wget | ≥ 1.20 | `apt install wget` | https://www.gnu.org/software/wget/ |
| UFW | ≥ 0.36 | `apt install ufw` | https://wiki.ubuntu.com/UncomplicatedFirewall |
| fail2ban | ≥ 0.11 | `apt install fail2ban` | https://github.com/fail2ban/fail2ban |
| auditd | ≥ 3.0 | `apt install auditd audispd-plugins` | https://people.redhat.com/sgrubb/audit/ |
| AIDE | ≥ 0.17 | `apt install aide` | https://aide.github.io/ |
| Lynis | ≥ 3.0 | `apt install lynis` | https://cisofy.com/lynis/ |
| rkhunter | ≥ 1.4 | `apt install rkhunter` | https://rkhunter.sourceforge.net/ |
| ClamAV | ≥ 0.103 | `apt install clamav clamav-daemon` | https://www.clamav.net/downloads |
| Hermes Agent | v0.16.0 | `curl -fsSL https://hermes-agent.nousresearch.com/install.sh \| sh` | https://hermes-agent.nousresearch.com/install.sh |
| Chromium | ≥ 120 | `apt install chromium-browser` | https://www.chromium.org/ |

---

## Development Tools

| Tool | Version | Install Method | Link |
|------|---------|---------------|------|
| Python3 | ≥ 3.10 | `apt install python3 python3-pip python3-venv` | https://www.python.org/downloads/ |
| pip | ≥ 22 | `apt install python3-pip` | https://pypi.org/project/pip/ |
| pipx | ≥ 1.0 | `apt install pipx` | https://pypa.github.io/pipx/ |
| Go (golang) | ≥ 1.21 | `wget https://go.dev/dl/go1.22.2.linux-amd64.tar.gz && tar -C /usr/local -xzf go*.tar.gz && export PATH=$PATH:/usr/local/go/bin` | https://go.dev/dl/ |
| Node.js | ≥ 20 (LTS) | Via NVM: `nvm install --lts` | https://nodejs.org/ |
| NVM | ≥ 0.39 | `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh \| bash` | https://github.com/nvm-sh/nvm |
| npm | ≥ 10 | Included with Node.js | https://www.npmjs.com/ |
| Playwright | ≥ 1.40 | `pip install playwright && playwright install chromium` | https://playwright.dev/python/ |

---

## Security Tools

| Tool | Version | Install Method | Link |
|------|---------|---------------|------|
| nuclei | ≥ 3.2 | Via Go: `go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest` | https://github.com/projectdiscovery/nuclei |
| subfinder | ≥ 2.6 | Via Go: `go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest` | https://github.com/projectdiscovery/subfinder |
| httpx | ≥ 1.6 | Via Go: `go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest` | https://github.com/projectdiscovery/httpx |

---

## Automation Tools

| Tool | Version | Install Method | Link |
|------|---------|---------------|------|
| Hermes Agent | v0.16.0 | see System Tools | https://hermes-agent.nousresearch.com |
| Hermes Cron | built-in | Included with Hermes Agent | — |
| OpenSSH Server | ≥ 8.9 | `apt install openssh-server` | https://www.openssh.com/ |
| systemd | ≥ 247 | Built into Ubuntu/Debian | https://systemd.io/ |
| cron | ≥ 3.0 | `apt install cron` | https://github.com/chrony/chrony |
| rsync | ≥ 3.2 | `apt install rsync` | https://rsync.samba.org/ |
| tar | ≥ 1.34 | Built into Ubuntu/Debian | https://www.gnu.org/software/tar/ |
| gzip | ≥ 1.10 | Built into Ubuntu/Debian | https://www.gnu.org/software/gzip/ |

---

## Python Packages

| Package | Install Method | Purpose |
|---------|---------------|---------|
| `playwright` | `pip install playwright` | Browser automation |
| `requests` | `pip install requests` | HTTP API calls |
| `httpx` | `pip install httpx` | Async HTTP client |
| `aiohttp` | `pip install aiohttp` | Async HTTP server/client |
| `psutil` | `pip install psutil` | System monitoring (CPU, RAM, disk) |
| `schedule` | `pip install schedule` | In-process task scheduling |
| `python-dotenv` | `pip install python-dotenv` | `.env` file loading |
| `rich` | `pip install rich` | CLI pretty-printing |
| `sqlalchemy` | `pip install sqlalchemy` | Database ORM |
| `pydantic` | `pip install pydantic` | Data validation |

---

## Quick Install Commands

```bash
# ── System Essentials ──
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget ufw fail2ban auditd audispd-plugins aide lynis rkhunter clamav clamav-daemon chromium-browser openssh-server cron rsync

# ── Python ──
sudo apt install -y python3 python3-pip python3-venv
pip3 install --user pipx
pipx ensurepath

# ── NVM + Node.js ──
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install --lts

# ── Go ──
wget https://go.dev/dl/go1.22.2.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.22.2.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> ~/.bashrc
source ~/.bashrc

# ── Security Tools (Go-based) ──
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# ── Hermes Agent ──
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | sh

# ── Playwright ──
pip install playwright
playwright install chromium

# ── ClamAV Update ──
sudo freshclam
sudo systemctl enable clamav-daemon --now
```

---

## Version Check Commands

```bash
hermes --version    # Hermes Agent
python3 --version   # Python3
pip3 --version      # pip
go version          # Go
node --version      # Node.js
nvm --version       # NVM
git --version       # Git
curl --version      # curl
wget --version      # wget
nuclei -version     # nuclei
subfinder -version  # subfinder
httpx -version      # httpx
playwright --version # Playwright
chromium --version  # Chromium
ufw --version       # UFW
fail2ban-client --version  # fail2ban
auditctl -V         # auditd
aide --version      # AIDE
lynis --version     # Lynis
rkhunter --version  # rkhunter
clamscan --version  # ClamAV
```
