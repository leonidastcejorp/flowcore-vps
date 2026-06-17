# 🔧 Tools — Manual Install via Terminal
> **VPS:** grace-ku-sayang | **OS:** Ubuntu 24.04 LTS  
> **Dibuat:** $(date "+%d %b %Y")  
> **Catatan:** Centang `[x]` kalo udah keinstall biar tau progres

---

## ✅ SUDAH TERINSTAL (skip)
| Tool | Versi | Lokasi |
|------|-------|--------|
| Go | 1.22.5 | `/usr/local/go/bin/` |
| Node.js | v22.22.3 | `/root/.hermes/node/bin/` |
| Python 3 | 3.11.15 | venv Hermes |
| Git | 2.43.0 | `/usr/bin/git` |
| PM2 | 7.0.1 | `/usr/local/bin/pm2` |
| Yarn | 1.22.22 | `/usr/local/bin/yarn` |
| nuclei | latest | `~/go/bin/nuclei` |
| subfinder | latest | `~/go/bin/subfinder` |
| httpx (PD) | latest | `~/go/bin/httpx` |
| jq | 1.7 | `/usr/bin/jq` |
| htop | 3.3.0 | `/usr/bin/htop` |
| tmux | 3.4 | `/usr/bin/tmux` |
| ripgrep | 14.1.0 | `/usr/bin/rg` |
| ffmpeg | 6.1.1 | `/usr/bin/ffmpeg` |
| lsof | - | `/usr/bin/lsof` |
| ss (iproute2) | 6.1.0 | `/usr/bin/ss` |

---

## ❌ PERLU INSTALL MANUAL

### 📦 Package Managers & Core Utils
- [ ] **uv** — Python package manager (super fast, Rust-based)
      ```bash
      curl -LsSf https://astral.sh/uv/install.sh | sh
      ```
- [ ] **bat** — `cat` with syntax highlighting
      ```bash
      apt install bat -y
      ```
- [ ] **fzf** — fuzzy finder (life-changer buat CLI)
      ```bash
      git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
      ~/.fzf/install
      ```
- [ ] **fd** — better `find`
      ```bash
      apt install fd-find -y
      ```
- [ ] **duf** — disk usage info (better than `df`)
      ```bash
      apt install duf -y
      ```
- [ ] **ncdu** — disk usage TUI (navigate & delete)
      ```bash
      apt install ncdu -y
      ```
- [ ] **btop** — resource monitor (better than htop)
      ```bash
      apt install btop -y
      ```
- [ ] **fastfetch** — system info (replacement buat neofetch)
      ```bash
      apt install fastfetch -y
      ```
- [ ] **chafa** — convert image ke ASCII/ANSI di terminal
      ```bash
      apt install chafa -y
      ```
- [ ] **csvkit** — CSV tools (csvcut, csvstat, csvlook, etc.)
      ```bash
      pip install csvkit
      ```
- [ ] **yt-dlp** — download video dari YouTube/dll
      ```bash
      apt install yt-dlp -y
      ```

### 🛡️ Security & Recon (Go tools)
- [ ] **naabu** — port scanner (projectdiscovery)
      ```bash
      go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
      ```
- [ ] **ffuf** — web fuzzer (FUZZ)
      ```bash
      go install github.com/ffuf/ffuf/v2@latest
      ```
- [ ] **gau** — get all URLs (tomnomnom)
      ```bash
      go install github.com/lc/gau/v2/cmd/gau@latest
      ```
- [ ] **waybackurls** — fetch URLs from Wayback Machine
      ```bash
      go install github.com/tomnomnom/waybackurls@latest
      ```
- [ ] **anew** — append new lines to file (tomnomnom)
      ```bash
      go install github.com/tomnomnom/anew@latest
      ```
- [ ] **katana** — web crawler (projectdiscovery)
      ```bash
      go install github.com/projectdiscovery/katana/cmd/katana@latest
      ```
- [ ] **gobuster** — directory/file/DNS brute force
      ```bash
      go install github.com/OJ/gobuster/v3@latest
      ```
- [ ] **amass** — subdomain enumeration (OWASP)
      ```bash
      go install github.com/owasp-amass/amass/v4/...@master
      ```
- [ ] **notify** — send notifications (projectdiscovery)
      ```bash
      go install github.com/projectdiscovery/notify/cmd/notify@latest
      ```
- [ ] **interactsh-client** — out-of-band interaction client
      ```bash
      go install github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest
      ```
- [ ] **uncover** — search engine recon (shodan, censys, etc.)
      ```bash
      go install github.com/projectdiscovery/uncover/cmd/uncover@latest
      ```

### 🐳 Container & Orchestration
- [ ] **docker** — container runtime
      ```bash
      apt install docker.io -y
      systemctl enable --now docker
      ```

---

## ⚡ CARA INSTALL BATCH (satu perintah)

Kalo males copy satu-satu, jalanin ini buat install **semua Go tools** sekaligus:

```bash
# Go tools batch install
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest && \
go install github.com/ffuf/ffuf/v2@latest && \
go install github.com/lc/gau/v2/cmd/gau@latest && \
go install github.com/tomnomnom/waybackurls@latest && \
go install github.com/tomnomnom/anew@latest && \
go install github.com/projectdiscovery/katana/cmd/katana@latest && \
go install github.com/OJ/gobuster/v3@latest && \
go install github.com/projectdiscovery/notify/cmd/notify@latest && \
go install github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest && \
go install github.com/projectdiscovery/uncover/cmd/uncover@latest
```

**Note:** `amass` gue pisahin karena cukup berat — jalanin sendiri kalo perlu.

```bash
# Apt batch install (core utils)
apt install -y bat fd-find duf ncdu btop fastfetch chafa yt-dlp docker.io
```

---

## 📍 PATH Notes
Semua Go tools otomatis ke `~/go/bin/`. Pastiin PATH lo udah include:
```bash
export PATH=$PATH:$HOME/go/bin
```
Kalo belum ada di `~/.bashrc` / `~/.zshrc`, tambahin:
```bash
echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.bashrc
source ~/.bashrc
```
