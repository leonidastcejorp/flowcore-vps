# FlowCore 🔄

> **Enterprise Workflow Automation Toolkit**
> Streamline your web operations with intelligent browser automation, data collection, and task orchestration.

---

## 🎯 Overview

FlowCore is a modular automation framework designed for:
- **Web task automation** — Form filling, account management, data entry
- **Intelligent data collection** — Structured web scraping with anti-detection
- **Workflow orchestration** — Scheduled pipelines, proxy management, monitoring
- **Identity management** — Secure multi-account lifecycle automation

Built on Playwright with advanced fingerprint spoofing and proxy rotation.

## ✨ Features

| Module | Description | Status |
|--------|-------------|--------|
| **Registrar** | Browser-based form automation with stealth | ✅ Stable |
| **Proxy Manager** | Rotating proxy pool with health checks | ✅ Stable |
| **Scraper** | Structured data extraction | 🔄 In dev |
| **Watcher** | Cron-based pipeline monitoring | ✅ Stable |
| **Fingerprint** | Browser fingerprint spoofing engine | ✅ Stable |

## 📖 Documentation

See the [Tutorial Guide](docs/TUTORIAL.md) for complete usage instructions, including:
- Account creation with the Registrar module
- Web scraping with anti-detection
- Proxy configuration and management
- Browser fingerprint spoofing
- Troubleshooting common issues

## 🚀 Quick Start

```bash
# Clone & install
git clone https://github.com/leonidastcejorp/flowcore.git
cd flowcore
pip install -r requirements.txt

# Run the pipeline
python -m flowcore.modules.registrar --help
```

## 📦 Installation

```bash
pip install -r requirements.txt
playwright install chromium
```

## ⚙️ Configuration

Edit `config/config.yaml` to customize:
- Target URLs and form selectors
- Proxy rotation settings
- Browser fingerprint profiles
- Cron schedules

## 🧩 Module Reference

### Browser Core (`flowcore.core.browser`)
Playwright wrapper with stealth configuration and proxy support.

### Fingerprint Engine (`flowcore.core.fingerprint`)  
Advanced browser fingerprint spoofing — WebGL, canvas, audio, fonts.

### Registrar (`flowcore.modules.registrar`)
Form automation module — configurable field mapping, validation, and submission.

### Proxy Manager (`flowcore.utils.network`)
Proxy pool management with automated health checks and rotation.

## 🛡️ Security

- All credentials encrypted at rest
- Proxy rotation prevents IP-based correlation
- Fingerprint randomization per session
- No persistent browser cache/storage

## 📄 License

MIT — See [LICENSE](LICENSE) for details.

---

*Built with Playwright · Python 3.11+ · Linux / macOS / Windows*
