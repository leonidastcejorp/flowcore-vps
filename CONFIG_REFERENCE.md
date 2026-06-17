# CONFIG_REFERENCE.md — Hermes Agent Configuration Reference

> File referensi lengkap tentang struktur konfigurasi Hermes Agent.
> Berlaku untuk Hermes Agent v0.16.0.
> Config file: `~/.hermes/config.yaml` (atau `$HERMES_HOME/config.yaml`)
> Env file: `~/.hermes/.env` (API keys & secrets)

---

## 📁 Lokasi File Konfigurasi

| File | Path | Deskripsi |
|------|------|-----------|
| Main Config | `~/.hermes/config.yaml` | Semua konfigurasi tools, terminal, providers, dll. |
| Env / Secrets | `~/.hermes/.env` | API keys dan secrets, auto-loaded dari sini. |
| Auth Tokens | `~/.hermes/auth.json` | OAuth tokens dan credential pools. |
| Session State | `~/.hermes/state.db` | SQLite database untuk session storage. |
| Logs | `~/.hermes/logs/` | Gateway dan error logs. |
| Cron Jobs | `~/.hermes/cron/jobs.json` | Daftar cron job (JSON). |
| Deployed Crons | `~/.hermes/.deployed_crons` | State file untuk tracking cron deployment. |
| State DB | `~/.hermes/state.db` | Canonical session store (SQLite + FTS5). |
| Source | `~/.hermes/hermes-agent/` | Source code (jika diinstall via git). |

---

## 📋 Config Sections Lengkap

### 1. `model` — Model AI Utama

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `model.default` | ✅ WAJIB | — | Nama model utama (e.g., `deepseek/deepseek-v4-flash`) |
| `model.provider` | ✅ WAJIB | — | Provider (`custom`, `openrouter`, `anthropic`, dll.) |
| `model.base_url` | ✅ WAJIB* | — | Custom API endpoint (*wajib kalo provider=custom) |
| `model.api_key` | ✅ WAJIB* | — | API key untuk provider (*bisa via .env) |
| `model.context_length` | ❌ Opsional | auto-detect | Override context length token |

**Contoh:**
```yaml
model:
  default: deepseek/deepseek-v4-flash
  provider: custom
  base_url: https://api.orcarouter.ai/v1
  api_key: sk-orc...v3Ur
```

---

### 2. `providers` — Definisi Provider Tambahan

| Key | Wajib? | Deskripsi |
|-----|--------|-----------|
| `providers` | ❌ Opsional | Mapping nama provider ke konfigurasi (base_url, api_key) |
| `fallback_providers` | ❌ Opsional | Daftar provider fallback |
| `credential_pool_strategies` | ❌ Opsional | Strategi pool credential |

---

### 3. `agent` — Perilaku Agent

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `agent.max_turns` | ❌ Opsional | 90 | Maksimal turn per session |
| `agent.gateway_timeout` | ❌ Opsional | 1800 | Timeout gateway (detik) |
| `agent.restart_drain_timeout` | ❌ Opsional | 180 | Timeout drain restart |
| `agent.api_max_retries` | ❌ Opsional | 3 | Retry maksimal API call |
| `agent.tool_use_enforcement` | ❌ Opsional | auto | Enforcement penggunaan tools |
| `agent.task_completion_guidance` | ❌ Opsional | true | Guidance completion task |
| `agent.environment_probe` | ❌ Opsional | true | Probe environment otomatis |
| `agent.reasoning_effort` | ❌ Opsional | medium | Effort reasoning (`low`/`medium`/`high`) |
| `agent.personalities` | ❌ Opsional | — | Daftar personality templates |
| `agent.image_input_mode` | ❌ Opsional | auto | Mode input gambar |
| `agent.gateway_auto_continue_freshness` | ❌ Opsional | 3600 | Auto-continue freshness (detik) |
| `agent.disabled_toolsets` | ❌ Opsional | [] | Toolset yang dinonaktifkan |

---

### 4. `terminal` — Terminal & Shell Backend

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `terminal.backend` | ❌ Opsional | local | Backend: `local`, `docker`, `ssh`, `modal` |
| `terminal.modal_mode` | ❌ Opsional | auto | Mode Modal |
| `terminal.cwd` | ❌ Opsional | . | Working directory default |
| `terminal.timeout` | ❌ Opsional | 180 | Timeout perintah (detik) |
| `terminal.docker_image` | ❌ Opsional | python-nodejs | Docker image untuk container |
| `terminal.container_cpu` | ❌ Opsional | 1 | CPU container |
| `terminal.container_memory` | ❌ Opsional | 5120 | Memory container (MB) |
| `terminal.container_disk` | ❌ Opsional | 51200 | Disk container (MB) |
| `terminal.persistent_shell` | ❌ Opsional | true | Persistent shell antar perintah |
| `terminal.auto_source_bashrc` | ❌ Opsional | true | Auto-source .bashrc |

---

### 5. `web` — Web Search & Scraping

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `web.backend` | ❌ Opsional | firecrawl | Backend web tools (`firecrawl`, dll.) |
| `web.search_backend` | ❌ Opsional | '' | Backend search spesifik |
| `web.extract_backend` | ❌ Opsional | '' | Backend extraction spesifik |
| `web.use_gateway` | ❌ Opsional | true | Gunakan gateway proxy |

---

### 6. `browser` — Browser Automation

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `browser.engine` | ❌ Opsional | auto | Engine: `auto`, `playwright`, `browserbase`, `camofox` |
| `browser.inactivity_timeout` | ❌ Opsional | 120 | Timeout inaktivitas (detik) |
| `browser.command_timeout` | ❌ Opsional | 30 | Timeout command (detik) |
| `browser.cloud_provider` | ❌ Opsional | browser-use | Cloud provider untuk browser |
| `browser.use_gateway` | ❌ Opsional | true | Gunakan gateway proxy |

---

### 7. `approvals` — Approval & Security Prompts

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `approvals.mode` | ❌ Opsional | manual | Mode: `manual`, `smart`, `off` |
| `approvals.timeout` | ❌ Opsional | 60 | Timeout approval (detik) |
| `approvals.cron_mode` | ❌ Opsional | deny | Mode approval untuk cron: `deny`, `allow` |

---

### 8. `security` — Keamanan

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `security.redact_secrets` | ❌ Opsional | true | Redact API keys dari output |
| `security.tirith_enabled` | ❌ Opsional | true | Enable Tirith policy engine |
| `security.website_blocklist` | ❌ Opsional | {} | Blocklist website |
| `security.allow_private_urls` | ❌ Opsional | false | Allow akses URL private |
| `security.allow_lazy_installs` | ❌ Opsional | true | Allow instalasi otomatis tools |

---

### 9. `memory` — Persistent Memory

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `memory.memory_enabled` | ❌ Opsional | true | Enable persistent memory |
| `memory.user_profile_enabled` | ❌ Opsional | true | Enable user profiling |
| `memory.write_approval` | ❌ Opsional | false | Require approval untuk write memory |
| `memory.memory_char_limit` | ❌ Opsional | 2200 | Max karakter per memory entry |
| `memory.provider` | ❌ Opsional | '' | Provider memory (kosong = default) |

---

### 10. `delegation` — Subagent Delegation

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `delegation.model` | ❌ Opsional | '' | Model untuk subagent |
| `delegation.provider` | ❌ Opsional | '' | Provider untuk subagent |
| `delegation.base_url` | ❌ Opsional | '' | Base URL untuk subagent |
| `delegation.api_key` | ❌ Opsional | '' | API key untuk subagent |
| `delegation.max_iterations` | ❌ Opsional | 50 | Max iterasi subagent |
| `delegation.max_concurrent_children` | ❌ Opsional | 3 | Max child concurrent |
| `delegation.max_spawn_depth` | ❌ Opsional | 1 | Max depth spawn subagent |
| `delegation.orchestrator_enabled` | ❌ Opsional | true | Enable orchestrator mode |

---

### 11. `compression` — Context Compression

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `compression.enabled` | ❌ Opsional | true | Enable context compression |
| `compression.threshold` | ❌ Opsional | 0.35 | Threshold kompresi (0.0 - 1.0) |
| `compression.target_ratio` | ❌ Opsional | 0.2 | Target ratio setelah kompresi |
| `compression.protect_last_n` | ❌ Opsional | 20 | Protect N turn terakhir |
| `compression.hygiene_hard_message_limit` | ❌ Opsional | 400 | Hard limit message |

---

### 12. `display` — Tampilan & UI

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `display.skin` | ❌ Opsional | default | Tema UI |
| `display.tool_progress` | ❌ Opsional | all | Tampilkan progress tools |
| `display.show_reasoning` | ❌ Opsional | false | Tampilkan reasoning |
| `display.show_cost` | ❌ Opsional | false | Tampilkan biaya per turn |
| `display.streaming` | ❌ Opsional | true | Enable streaming output |
| `display.language` | ❌ Opsional | en | Bahasa UI |
| `display.personality` | ❌ Opsional | '' | Personality default |
| `display.platforms` | ❌ Opsional | — | Konfigurasi per-platform (telegram, discord, dll.) |

---

### 13. `tts` — Text-to-Speech

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `tts.provider` | ❌ Opsional | openai | Provider: `edge`, `elevenlabs`, `openai`, `minimax`, `mistral`, `neutts` |
| `tts.use_gateway` | ❌ Opsional | true | Gunakan gateway proxy |

**API Key yang diperlukan:**
- `VOICE_TOOLS_OPENAI_KEY` untuk OpenAI TTS
- `ELEVENLABS_API_KEY` untuk ElevenLabs
- `MINIMAX_API_KEY` untuk MiniMax
- `MISTRAL_API_KEY` untuk Mistral

---

### 14. `stt` — Speech-to-Text

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `stt.enabled` | ❌ Opsional | true | Enable STT |
| `stt.provider` | ❌ Opsional | local | Provider: `local`, `groq`, `openai`, `mistral` |
| `stt.use_gateway` | ❌ Opsional | true | Gunakan gateway proxy |

**API Key yang diperlukan:**
- `GROQ_API_KEY` untuk Groq Whisper
- `VOICE_TOOLS_OPENAI_KEY` untuk OpenAI Whisper
- `MISTRAL_API_KEY` untuk Mistral

---

### 15. `cron` — Scheduled Jobs

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `cron.wrap_response` | ❌ Opsional | true | Wrap response dengan header/footer |
| `cron.max_parallel_jobs` | ❌ Opsional | null | Max parallel job (null = unlimited) |

---

### 16. `skills` — Skill Management

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `skills.external_dirs` | ❌ Opsional | [] | Direktori skill eksternal |
| `skills.template_vars` | ❌ Opsional | true | Enable template variables |
| `skills.inline_shell` | ❌ Opsional | false | Enable inline shell di skills |
| `skills.guard_agent_created` | ❌ Opsional | false | Guard skill created by agent |
| `skills.write_approval` | ❌ Opsional | false | Require approval untuk write skill |

---

### 17. `curator` — Skill Lifecycle Curator

| Key | Wajib? | Default | Deskripsi |
|-----|--------|---------|-----------|
| `curator.enabled` | ❌ Opsional | true | Enable curator |
| `curator.interval_hours` | ❌ Opsional | 168 | Interval maintenance (jam) |
| `curator.stale_after_days` | ❌ Opsional | 30 | Tandai stale setelah N hari |
| `curator.archive_after_days` | ❌ Opsional | 90 | Archive setelah N hari |

---

### 18. `auxiliary` — Auxiliary Model Config

Sub-section untuk berbagai sub-system yang butuh model sendiri:

| Sub-section | Kegunaan |
|-------------|----------|
| `auxiliary.vision` | Model untuk analisis gambar |
| `auxiliary.web_extract` | Model untuk web extraction |
| `auxiliary.compression` | Model untuk context compression |
| `auxiliary.skills_hub` | Model untuk skills hub |
| `auxiliary.approval` | Model untuk smart approval |
| `auxiliary.mcp` | Model untuk MCP |
| `auxiliary.title_generation` | Model untuk generate judul |
| `auxiliary.triage_specifier` | Model untuk triage |
| `auxiliary.curator` | Model untuk curator |
| `auxiliary.monitor` | Model untuk monitoring |

Masing-masing punya key: `provider`, `model`, `base_url`, `api_key`, `timeout`.

---

### 19. Platform Integrations

| Section | Platform | Key Config |
|---------|----------|------------|
| `telegram` | Telegram Bot | `reactions`, `allowed_chats`, `parse_mode` |
| `discord` | Discord Bot | `require_mention`, `auto_thread`, `reactions` |
| `slack` | Slack App | `require_mention`, `allowed_channels` |
| `whatsapp` | WhatsApp | `{}` (env-based) |
| `matrix` | Matrix | `require_mention`, `allowed_rooms` |
| `mattermost` | Mattermost | `require_mention`, `allowed_channels` |

---

### 20. Lainnya

| Section | Deskripsi |
|---------|-----------|
| `gateway` | Gateway configuration (`strict`, `media_delivery_allow_dirs`) |
| `logging` | Log level & rotation (`level`, `max_size_mb`, `backup_count`) |
| `sessions` | Session management (`retention_days`, `auto_prune`) |
| `checkpoints` | Session checkpointing (`enabled`, `max_snapshots`) |
| `kanban` | Multi-agent work queue (`dispatch_in_gateway`, `failure_limit`) |
| `code_execution` | Sandboxed Python execution (`mode`, `timeout`) |
| `streaming` | Output streaming (`enabled`, `transport`) |
| `secrets` | Secret management (Bitwarden integration) |
| `plugins` | Plugin management (`enabled`) |
| `timezone` | Timezone setting (e.g., `Asia/Jakarta`) |
| `hooks` | Pre/post execution hooks |
| `tools` | Tool configuration (`tool_search`) |
| `image_gen` | Image generation settings |
| `model_catalog` | Model catalog settings |
| `updates` | Auto-update configuration |
| `lsp` | Language Server Protocol integration |
| `network` | Network settings |
| `command_allowlist` | Allowlisted destructive commands |
| `custom_providers` | Custom provider definitions |
| `platform_toolsets` | Toolset mapping per platform |

---

## 🔑 API Keys — Yang WAJIB Diisi

| Key | Env Variable | Keperluan | Wajib? |
|-----|-------------|-----------|--------|
| Model API Key | `model.api_key` di config atau `.env` | Akses ke LLM provider | ✅ WAJIB |
| OpenRouter | `OPENROUTER_API_KEY` | Router ke berbagai model | ❌ (alternatif) |
| Anthropic | `ANTHROPIC_API_KEY` | Claude models | ❌ (alternatif) |
| DeepSeek | `DEEPSEEK_API_KEY` | DeepSeek models | ❌ (alternatif) |
| Google/Gemini | `GOOGLE_API_KEY` / `GEMINI_API_KEY` | Gemini models | ❌ |
| xAI/Grok | `XAI_API_KEY` | Grok models | ❌ |
| OpenAI TTS | `VOICE_TOOLS_OPENAI_KEY` | Text-to-speech OpenAI | ❌ |
| ElevenLabs | `ELEVENLABS_API_KEY` | Text-to-speech ElevenLabs | ❌ |
| MiniMax | `MINIMAX_API_KEY` | TTS atau model | ❌ |
| Groq | `GROQ_API_KEY` | STT (Whisper) via Groq | ❌ |
| Mistral | `MISTRAL_API_KEY` | STT/TTS Mistral | ❌ |
| Hugging Face | `HF_TOKEN` | Hugging Face models | ❌ |
| GitHub Copilot | `COPILOT_GITHUB_TOKEN` | Copilot integration | ❌ |
| Z.AI / GLM | `ZAI_API_KEY` / `GLM_API_KEY` | GLM models | ❌ |
| Kimi | `KIMI_API_KEY` | Moonshot/Kimi models | ❌ |
| Alibaba | `DASHSCOPE_API_KEY` | Qwen/DashScope | ❌ |

---

## 🧩 Profiles

Setiap profile memiliki struktur folder sendiri di `~/.hermes/profiles/<nama>/`:

```
~/.hermes/profiles/<nama>/
├── config.yaml        # Profile-specific config
├── .env               # Profile-specific secrets
├── skills/            # Profile-specific skills
├── plugins/           # Profile-specific plugins
├── cron/              # Profile-specific cron jobs
└── memories/          # Profile-specific memories
```

**Cara pakai:**
```bash
hermes --profile work        # Run dengan profile "work"
hermes --profile default     # Run dengan profile default
```

Profile berbeda berarti session, skills, plugins, cron, dan memory terisolasi.

---

## 🧩 Skills

Skills adalah modul yang memberikan Hermes pengetahuan domain spesifik.

**Lokasi:**
- Built-in: `~/.hermes/skills/autonomous-ai-agents/` (bundled)
- Installed: `~/.hermes/skills/` (via `hermes skills install`)
- Custom: via `skills.external_dirs` di config.yaml

**Struktur skill:**
```
skill-name/
├── SKILL.md           # Main skill definition
├── references/        # Referensi & dokumentasi
│   └── *.md
└── scripts/           # Script pendukung
    └── *.py / *.sh
```

**Manajemen:**
```bash
hermes skills list              # List installed skills
hermes skills install <name>    # Install skill dari hub
hermes skills remove <name>     # Remove skill
hermes skills create <name>     # Create skill sendiri
```

---

## 🔌 Plugins

Plugins menambahkan toolsets kustom ke Hermes.

**Lokasi:** `~/.hermes/plugins/`

**Config:**
```yaml
plugins:
  enabled: null        # null = all enabled, atau daftar plugin spesifik
```

**Manajemen:**
```bash
hermes plugins list              # List installed plugins
hermes plugins install <name>    # Install plugin
hermes plugins remove <name>     # Remove plugin
```

---

## 🛠️ Toolsets

Toolsets adalah grup tools yang bisa di-enable/disable per platform.

| Toolset | Fungsi |
|---------|--------|
| `web` | Web search & content extraction |
| `browser` | Browser automation |
| `terminal` | Shell commands & process management |
| `file` | File read/write/search/patch |
| `code_execution` | Sandboxed Python execution |
| `vision` | Image analysis |
| `image_gen` | AI image generation |
| `cronjob` | Scheduled task management |
| `delegation` | Subagent task delegation |
| `memory` | Persistent cross-session memory |
| `messaging` | Cross-platform message sending |
| `skills` | Skill browsing & management |

**Config per platform** (di `platform_toolsets`):
```yaml
platform_toolsets:
  cli:
    - browser
    - terminal
    - file
    - web
    # ...
  telegram:
    - browser
    - terminal
    # ...
```

---

## 📝 Cara Edit Config

```bash
# Buka config di editor
hermes config edit

# Set nilai spesifik
hermes config set agent.max_turns 150
hermes config set display.show_cost true
hermes config set timezone Asia/Jakarta

# Get nilai
hermes config get agent.max_turns

# Lihat path config
hermes config path
```

> **Catatan:** Agent tidak bisa mengedit config.yaml langsung dari tool call. 
> Edit manual atau gunakan `hermes config set` dari terminal.

---

## 🔗 Referensi

- Dokumentasi resmi: https://hermes-agent.nousresearch.com/docs/user-guide/configuration
- Provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers
- Cron docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/cron
- Skill docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
