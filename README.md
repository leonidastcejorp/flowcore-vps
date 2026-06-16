# FlowCore VPS Backup

> **Backup lengkap VPS grace-ku-sayang** — Hermes Agent + monitoring + automation tools.
> Support **Ubuntu 22.04** dan **24.04**.

## Quick Setup

```bash
git clone https://github.com/leonidastcejorp/flowcore-vps.git
cd flowcore-vps
bash pre-flight.sh   # Cek kondisi VPS
bash setup.sh        # Install semua (10-15 menit)
```

## OS Support

| Ubuntu | Catatan |
|--------|---------|
| **22.04 LTS** | Tested, kernel 5.15+, package names cocok |
| **24.04 LTS** | Tested, kernel 6.8+, setup.sh auto-detect beda package names |

Setup otomatis mendeteksi versi Ubuntu dan pakai package names yang sesuai.

## Isi Repo

- **Hermes Agent** v0.16.0 — config, scripts, cron, personality (BREACH)
- **Monitoring Suite** — 12 cron jobs, resource watchdog, Telegram alerts
- **FlowCore Toolkit** — Browser automation, form registrar, scraper
- **Ghost Framework** — Mass account creator (Discord, Fiverr, Reddit)
- **Security Tools** — nuclei, subfinder, httpx, fail2ban, lynis
- **Backup Scripts** — VPS backup, proxy updater, income pipeline

## Post-Install

1. **API Keys** — Isi di `~/.hermes/.env` atau `~/.hermes/config.yaml`
2. **Cron Jobs** — `bash deploy-cron.sh` (12 jobs, NO-AGENT mode)
3. **Verify** — `hermes status`, `nuclei -version`, `playwright --version`
4. **Reboot** — `sudo reboot`

## Channel

- Telegram group: `-1003534226714` (Kantor FBI)
- Personal chat: `5695981991`

---

*Hermes Agent v0.16.0 · deepseek/deepseek-v4-flash · Backup 2026-06-15*
