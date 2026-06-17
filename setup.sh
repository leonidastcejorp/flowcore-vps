#!/bin/bash
# ============================================================================
# ═╗ ╦╦╔═╗╦═╗  ═╗ ╦╦╔═╗╦═╗
# ╔╩╦╝║║ ╦╠╦╝  ╔╩╦╝║║ ╦╠╦╝
# ╩ ╚═╩╚═╝╩╚═  ╩ ╚═╩╚═╝╩╚═
#
# FlowCore VPS — FULL SETUP SCRIPT
# Supports Ubuntu 22.04 AND 24.04
# ============================================================================

# ── Configuration ──────────────────────────────────────────────────────────
HERMES_VERSION="v0.16.0"
HERMES_INSTALL_URL="https://hermes-agent.nousresearch.com/install.sh"
GO_VERSION="1.22.5"
NODE_VERSION="20"

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HERMES_DIR="$HOME/.hermes"
SCRIPTS_DIR="$REPO_DIR/hermes/scripts"
LOG_FILE="/tmp/flowcore-setup-$(date +%Y%m%d-%H%M%S).log"

# ── Tracking ───────────────────────────────────────────────────────────────
SUCCESS_STEPS=()
FAILED_STEPS=()

log() { echo -e "$1" | tee -a "$LOG_FILE"; }
ok()   { log "  ✅ $1"; SUCCESS_STEPS+=("$1"); }
fail() { log "  ❌ $1"; FAILED_STEPS+=("$1"); }

# ── Banner ─────────────────────────────────────────────────────────────────
show_banner() {
    clear 2>/dev/null || true
    cat << "EOF"
╔══════════════════════════════════════════════════════════════════════╗
║       FLOWCORE VPS — Full Environment Setup                         ║
║       Supports Ubuntu 22.04 & 24.04                                 ║
║       Hermes Agent ${HERMES_VERSION}                                     ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
    echo ""
}

# ── Confirmation Prompt ──────────────────────────────────────────────────
confirm_proceed() {
    echo "⚠️  This script will install/update the following:"
    echo "   • System packages (git, python3, curl, etc.)"
    echo "   • Hermes Agent ${HERMES_VERSION}"
    echo "   • Go ${GO_VERSION}"
    echo "   • Node.js ${NODE_VERSION} (via NVM)"
    echo "   • Security tools (nuclei, subfinder, httpx)"
    echo "   • Playwright + Chromium"
    echo "   • Hermes scripts, config, and cron jobs"
    echo "   • Hermes plugins"
    echo ""
    echo "📋 Log file: $LOG_FILE"
    echo ""
    
    # Run pre-flight first
    echo "━━━ Running pre-flight checks... ━━━"
    if [ -f "$REPO_DIR/pre-flight.sh" ]; then
        bash "$REPO_DIR/pre-flight.sh" | tee -a "$LOG_FILE"
        echo ""
        # Extract status from pre-flight JSON
        PREFLIGHT_STATUS=$(bash "$REPO_DIR/pre-flight.sh" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null)
        if [ "$PREFLIGHT_STATUS" = "blocked" ]; then
            echo "⚠️  Pre-flight checks indicate BLOCKED status."
            echo "   Some prerequisites may not be met."
            echo ""
            bash "$REPO_DIR/pre-flight.sh" 2>/dev/null | python3 -m json.tool 2>/dev/null || true
            echo ""
            read -rp "Continue anyway? (y/N): " CONTINUE
            if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
                echo "❌ Setup cancelled by user."
                exit 1
            fi
        fi
    fi

    read -rp "Proceed with setup? (y/N): " CONFIRM
    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled by user."
        exit 1
    fi
    echo ""
}

# ══════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════

# ── Pre-Flight ───────────────────────────────────────────────────────────
pre_flight_check() {
    log "━━━ [1/9] Pre-Flight Check ━━━"
    
    if [ ! -f "$REPO_DIR/pre-flight.sh" ]; then
        fail "pre-flight.sh not found in repo"
        return 1
    fi

    bash "$REPO_DIR/pre-flight.sh" 2>/dev/null > /tmp/flowcore-preflight.json
    
    # Parse and display
    if command -v python3 &>/dev/null; then
        python3 -c "
import json
with open('/tmp/flowcore-preflight.json') as f:
    d = json.load(f)
print(f'  OS: {d[\"os\"][\"version\"]} ({d[\"os\"][\"codename\"]})')
print(f'  RAM available: {d[\"ram_mb\"]} MB')
print(f'  Disk available: {d[\"disk_mb\"]} MB')
print(f'  Internet: {\"✅\" if d[\"internet\"] else \"❌\"}')
print(f'  Apt locked: {\"⚠️  Yes\" if d[\"apt_locked\"] else \"No\"}')
print(f'  Background updates: {\"⚠️  Yes\" if d[\"bg_updates\"] else \"No\"}')
print(f'  Status: {\"✅\" if d[\"status\"]==\"ready\" else \"⚠️  \"+d[\"status\"]}')
" 2>/dev/null || echo "  (parse error, see log)"
    fi
    
    ok "Pre-flight checks completed"
}

# ── System Packages ──────────────────────────────────────────────────────
install_system_packages() {
    log "━━━ [2/9] System Packages ━━━"

    # Detect OS version
    OS_VERSION="24.04"
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_VERSION="$VERSION_ID"
    fi

    log "  Detected Ubuntu ${OS_VERSION}"

    # Update package lists (non-blocking)
    apt update -y 2>/dev/null || log "  ⚠️ apt update had issues (may be transient)"

    # Base packages common to both versions
    BASE_PKGS="git python3 python3-pip python3-venv unzip curl wget ca-certificates gnupg lsb-release software-properties-common build-essential"

    # Ubuntu 22.04 needs python3.10-venv explicitly sometimes
    if [[ "$OS_VERSION" == "22.04" ]]; then
        log "  Using Ubuntu 22.04 package set"
        apt install -y $BASE_PKGS python3.10-venv 2>>"$LOG_FILE" || \
        apt install -y $BASE_PKGS 2>>"$LOG_FILE"
    else
        log "  Using Ubuntu 24.04 package set"
        apt install -y $BASE_PKGS 2>>"$LOG_FILE"
    fi

    # Verify python3
    if command -v python3 &>/dev/null; then
        ok "System packages installed (Python $(python3 --version 2>&1 | cut -d' ' -f2))"
    else
        fail "python3 not found after install"
    fi
}

# ── Hermes Agent ─────────────────────────────────────────────────────────
install_hermes_agent() {
    log "━━━ [3/9] Hermes Agent ━━━"

    if command -v hermes &>/dev/null; then
        INSTALLED_VER=$(hermes --version 2>/dev/null || echo "unknown")
        log "  Hermes already installed: $INSTALLED_VER"
        ok "Hermes Agent already installed"
        return 0
    fi

    log "  Installing Hermes Agent ${HERMES_VERSION}..."
    if curl -fsSL "$HERMES_INSTALL_URL" | bash 2>>"$LOG_FILE"; then
        # Source it
        export PATH="$HOME/.hermes/bin:$PATH"
        if command -v hermes &>/dev/null; then
            ok "Hermes Agent installed ($(hermes --version 2>/dev/null || echo 'version unknown'))"
        else
            fail "Hermes installed but 'hermes' command not found in PATH"
        fi
    else
        fail "Hermes Agent installation failed"
    fi
}

# ── Go Language ──────────────────────────────────────────────────────────
install_go() {
    log "━━━ [4/9] Go ${GO_VERSION} ━━━"

    if command -v go &>/dev/null && go version | grep -q "go${GO_VERSION}"; then
        ok "Go ${GO_VERSION} already installed"
        return 0
    fi

    log "  Downloading Go ${GO_VERSION}..."
    cd /tmp
    wget -q "https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz" -O "go${GO_VERSION}.linux-amd64.tar.gz" 2>>"$LOG_FILE" || {
        fail "Go download failed"
        return 1
    }

    rm -rf /usr/local/go
    tar -C /usr/local -xzf "go${GO_VERSION}.linux-amd64.tar.gz" 2>>"$LOG_FILE" || {
        fail "Go extraction failed"
        rm -f "go${GO_VERSION}.linux-amd64.tar.gz"
        return 1
    }
    rm -f "go${GO_VERSION}.linux-amd64.tar.gz"

    # Add to PATH if not already
    if ! grep -q '/usr/local/go/bin' ~/.bashrc 2>/dev/null; then
        echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    fi
    export PATH="$PATH:/usr/local/go/bin"

    if command -v go &>/dev/null && go version | grep -q "go${GO_VERSION}"; then
        ok "Go ${GO_VERSION} installed"
    else
        fail "Go installation verification failed"
    fi
}

# ── Node.js via NVM ──────────────────────────────────────────────────────
install_node_nvm() {
    log "━━━ [5/9] Node.js ${NODE_VERSION} (via NVM) ━━━"

    # Source NVM if available
    export NVM_DIR="$HOME/.nvm"
    if [ -s "$NVM_DIR/nvm.sh" ]; then
        \. "$NVM_DIR/nvm.sh"
    fi

    if command -v node &>/dev/null && node --version | grep -q "v${NODE_VERSION}"; then
        ok "Node.js v${NODE_VERSION} already installed"
        return 0
    fi

    # Install NVM if not present
    if [ ! -s "$NVM_DIR/nvm.sh" ]; then
        log "  Installing NVM..."
        curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash 2>>"$LOG_FILE" || {
            fail "NVM installation failed"
            return 1
        }
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    fi

    # Install Node via NVM
    log "  Installing Node.js v${NODE_VERSION}..."
    nvm install "${NODE_VERSION}" 2>>"$LOG_FILE" || {
        fail "Node.js v${NODE_VERSION} installation failed"
        return 1
    }
    nvm use "${NODE_VERSION}" 2>>"$LOG_FILE" || true
    nvm alias default "${NODE_VERSION}" 2>>"$LOG_FILE" || true

    if command -v node &>/dev/null; then
        ok "Node.js $(node --version) installed"
    else
        fail "Node.js verification failed"
    fi
}

# ── Security Tools (nuclei, subfinder, httpx) ────────────────────────────
install_security_tools() {
    log "━━━ [6/9] Security Tools ━━━"

    export PATH="$PATH:/usr/local/go/bin:$HOME/go/bin"
    export GOPATH="$HOME/go"

    # nuclei
    if ! command -v nuclei &>/dev/null; then
        log "  Installing nuclei..."
        go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest 2>>"$LOG_FILE" || {
            # Fallback: download binary directly
            wget -q "https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_3.3.9_linux_amd64.zip" -O /tmp/nuclei.zip 2>/dev/null && \
            unzip -q -o /tmp/nuclei.zip -d /tmp/nuclei 2>/dev/null && \
            cp /tmp/nuclei/nuclei /usr/local/bin/ 2>/dev/null && \
            rm -rf /tmp/nuclei* 2>/dev/null || \
            log "  ⚠️ nuclei install skipped"
        }
    fi
    if command -v nuclei &>/dev/null; then
        ok "nuclei installed ($(nuclei -version 2>&1 | head -1))"
    else
        fail "nuclei not installed"
    fi

    # subfinder
    if ! command -v subfinder &>/dev/null; then
        log "  Installing subfinder..."
        go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>>"$LOG_FILE" || \
        log "  ⚠️ subfinder install skipped"
    fi
    if command -v subfinder &>/dev/null; then
        ok "subfinder installed"
    else
        fail "subfinder not installed"
    fi

    # httpx
    if ! command -v httpx &>/dev/null; then
        log "  Installing httpx..."
        go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest 2>>"$LOG_FILE" || \
        log "  ⚠️ httpx install skipped"
    fi
    if command -v httpx &>/dev/null; then
        ok "httpx installed"
    else
        fail "httpx not installed"
    fi
}

# ── Playwright + Chromium ────────────────────────────────────────────────
install_playwright() {
    log "━━━ [7/9] Playwright & Chromium ━━━"

    pip3 install --upgrade pip 2>>"$LOG_FILE" || true
    pip3 install playwright aiohttp aiohttp-socks pyyaml 2>>"$LOG_FILE" || {
        fail "Python dependencies install failed"
        return 1
    }

    # Install Chromium via Playwright
    python3 -m playwright install chromium 2>>"$LOG_FILE" || {
        log "  Trying with system deps..."
        python3 -m playwright install --with-deps chromium 2>>"$LOG_FILE" || {
            log "  ⚠️ Playwright Chromium install had issues"
            log "  Install manually: playwright install --with-deps chromium"
            fail "Playwright Chromium installation"
            return 1
        }
    }

    ok "Playwright + Chromium installed"
}

# ── Hermes Config & Scripts ──────────────────────────────────────────────
setup_hermes_config() {
    log "━━━ [8/9] Hermes Config & Scripts ━━━"

    mkdir -p "$HERMES_DIR/scripts" "$HERMES_DIR/plugins" "$HERMES_DIR/cron"
    mkdir -p "$HERMES_DIR/scripts/lib"

    # Config
    if [ -f "$REPO_DIR/hermes/config.yaml" ]; then
        cp "$REPO_DIR/hermes/config.yaml" "$HERMES_DIR/config.yaml"
        ok "Hermes config copied"
        
        # Warn about API key
        if grep -q "YOUR_API_KEY" "$HERMES_DIR/config.yaml" 2>/dev/null; then
            log "  ⚠️  API key is still a placeholder (YOUR_API_KEY)"
            log "  🔑 Edit ~/.hermes/config.yaml and set your real API key"
        fi
    else
        fail "config.yaml not found in repo"
    fi

    # SOUL.md
    if [ -f "$REPO_DIR/hermes/SOUL.md" ]; then
        cp "$REPO_DIR/hermes/SOUL.md" "$HERMES_DIR/SOUL.md"
        ok "SOUL.md copied"
    fi
    if [ -f "$REPO_DIR/hermes/SOUL.backup.md" ]; then
        cp "$REPO_DIR/hermes/SOUL.backup.md" "$HERMES_DIR/SOUL.backup.md"
        ok "SOUL.backup.md copied"
    fi

    # Scripts
    if [ -d "$SCRIPTS_DIR" ]; then
        cp "$SCRIPTS_DIR"/*.py "$HERMES_DIR/scripts/" 2>/dev/null || true
        cp "$SCRIPTS_DIR"/*.sh "$HERMES_DIR/scripts/" 2>/dev/null || true
        # Lib
        if [ -d "$SCRIPTS_DIR/lib" ]; then
            cp "$SCRIPTS_DIR/lib"/*.py "$HERMES_DIR/scripts/lib/" 2>/dev/null || true
            cp "$SCRIPTS_DIR/lib"/*.sh "$HERMES_DIR/scripts/lib/" 2>/dev/null || true
        fi
        ok "Scripts copied to ~/.hermes/scripts/"
    else
        fail "Scripts directory not found in repo"
    fi

    # Plugins
    if [ -d "$REPO_DIR/hermes/plugins" ]; then
        cp -r "$REPO_DIR/hermes/plugins/"* "$HERMES_DIR/plugins/" 2>/dev/null || true
        ok "Plugins copied"
    fi

    # State DB (if exists)
    if [ -f "$REPO_DIR/hermes/state.db" ]; then
        cp "$REPO_DIR/hermes/state.db" "$HERMES_DIR/state.db"
        ok "state.db restored"
    fi

    # Permissions
    find "$HERMES_DIR/scripts" -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
    find "$HERMES_DIR/scripts" -type f -name "*.py" -exec chmod +x {} \; 2>/dev/null || true
}

# ── Deploy Cron ──────────────────────────────────────────────────────────
setup_deploy_cron() {
    log "━━━ [9/9] Cron Jobs ━━━"

    if [ ! -f "$REPO_DIR/hermes/cron/jobs.json" ]; then
        fail "cron/jobs.json not found in repo"
        return 1
    fi

    cp "$REPO_DIR/hermes/cron/jobs.json" "$HERMES_DIR/cron/jobs.json"
    ok "Cron jobs file copied"

    # Import via Hermes CLI if available
    if command -v hermes &>/dev/null; then
        log "  Importing cron jobs via Hermes CLI..."
        if hermes cron import "$HERMES_DIR/cron/jobs.json" 2>>"$LOG_FILE"; then
            ok "Cron jobs imported via Hermes CLI"
        else
            log "  ⚠️ Cron import failed (run manually: hermes cron import ~/.hermes/cron/jobs.json)"
            fail "Cron import via CLI"
        fi
    else
        log "  ⚠️ Hermes CLI not available — cron file copied but not imported"
        log "  Run manually: hermes cron import ~/.hermes/cron/jobs.json"
        fail "Cron import (hermes not available)"
    fi
}

# ── Summary ──────────────────────────────────────────────────────────────
show_summary() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║                    ✅ SETUP COMPLETE                                 ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📋 Summary:"
    echo "   ✅ ${#SUCCESS_STEPS[@]} steps succeeded"
    echo "   ❌ ${#FAILED_STEPS[@]} steps failed"
    echo ""

    if [ ${#SUCCESS_STEPS[@]} -gt 0 ]; then
        echo "   Successful:"
        for s in "${SUCCESS_STEPS[@]}"; do
            echo "     ✅ $s"
        done
        echo ""
    fi

    if [ ${#FAILED_STEPS[@]} -gt 0 ]; then
        echo "   Failed/Issues:"
        for f in "${FAILED_STEPS[@]}"; do
            echo "     ❌ $f"
        done
        echo ""
    fi

    echo "📝 Log file: $LOG_FILE"
    echo ""
    echo "🔑 IMPORTANT: Update API keys in ~/.hermes/config.yaml"
    echo "   Look for 'YOUR_API_KEY' and replace with real keys"
    echo ""
    echo "🔄 Reboot recommended to apply all sysctl changes:"
    echo "   sudo reboot"
    echo ""
}

# ══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ══════════════════════════════════════════════════════════════════════════

show_banner
confirm_proceed

# Run all steps
pre_flight_check
install_system_packages
install_hermes_agent
install_go
install_node_nvm
install_security_tools
install_playwright
setup_hermes_config
setup_deploy_cron

show_summary
