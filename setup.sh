#!/bin/bash
# ============================================================================
# ═╗ ╦╦╔═╗╦═╗  ═╗ ╦╦╔═╗╦═╗
# ╔╩╦╝║║ ╦╠╦╝  ╔╩╦╝║║ ╦╠╦╝
# ╩ ╚═╩╚═╝╩╚═  ╩ ╚═╩╚═╝╩╚═
#
# FlowCore VPS — FULL RESTORE SCRIPT
# Restores this exact Ubuntu 22.04 VPS environment
# ============================================================================
set -e

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║       FLOWCORE VPS — Full Environment Restore                      ║"
echo "║       Ubuntu 22.04 · 2c/2GB/40GB · Kernel 5.15.0-181-generic      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"

# ── Configuration ──────────────────────────────────────────────────────────
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📂 Restoring from: $REPO_DIR"

# ── 1. System Updates & Packages ───────────────────────────────────────────
echo ""
echo "━━━ [1/10] System Updates & Base Packages ━━━"
apt update -y
apt upgrade -y
apt install -y git python3 python3-pip python3-venv unzip curl wget ca-certificates gnupg lsb-release

# ── 2. DNS — Cloudflare 1.1.1.1 / 8.8.8.8 ─────────────────────────────────
echo ""
echo "━━━ [2/10] DNS Configuration ─━━"
cat > /etc/resolv.conf << 'EOF'
nameserver 1.1.1.1
nameserver 8.8.8.8
EOF
chattr +i /etc/resolv.conf 2>/dev/null || true
echo "✅ DNS set to 1.1.1.1 / 8.8.8.8"

# ── 3. Swappiness=10 ───────────────────────────────────────────────────────
echo ""
echo "━━━ [3/10] Swappiness Configuration ─━━"
sysctl vm.swappiness=10
echo "vm.swappiness=10" >> /etc/sysctl.conf
echo "✅ Swappiness set to 10"

# ── 4. Hermes Configuration ────────────────────────────────────────────────
echo ""
echo "━━━ [4/10] Hermes Configuration ─━━"
mkdir -p ~/.hermes/scripts ~/.hermes/plugins ~/.hermes/cron

if [ -f "$REPO_DIR/hermes/config.yaml" ]; then
    cp "$REPO_DIR/hermes/config.yaml" ~/.hermes/config.yaml
    echo "✅ Hermes config restored (API keys need manual update)"
fi
if [ -f "$REPO_DIR/hermes/SOUL.md" ]; then
    cp "$REPO_DIR/hermes/SOUL.md" ~/.hermes/SOUL.md
    echo "✅ SOUL.md restored"
fi
if [ -f "$REPO_DIR/hermes/SOUL.backup.md" ]; then
    cp "$REPO_DIR/hermes/SOUL.backup.md" ~/.hermes/SOUL.backup.md
    echo "✅ SOUL.backup.md restored"
fi
if [ -f "$REPO_DIR/hermes/state.db" ]; then
    cp "$REPO_DIR/hermes/state.db" ~/.hermes/state.db
    echo "✅ Hermes state.db restored"
fi

# Scripts
if [ -d "$REPO_DIR/hermes/scripts" ]; then
    cp "$REPO_DIR/hermes/scripts/"*.py ~/.hermes/scripts/ 2>/dev/null || true
    cp "$REPO_DIR/hermes/scripts/"*.sh ~/.hermes/scripts/ 2>/dev/null || true
    echo "✅ Hermes scripts restored"
fi

# Plugins
if [ -d "$REPO_DIR/hermes/plugins" ]; then
    cp -r "$REPO_DIR/hermes/plugins/"* ~/.hermes/plugins/ 2>/dev/null || true
    echo "✅ Hermes plugins restored"
fi

# Cron jobs
if [ -f "$REPO_DIR/hermes/cron/jobs.json" ]; then
    cp "$REPO_DIR/hermes/cron/jobs.json" ~/.hermes/cron/jobs.json
    echo "✅ Cron jobs restored"
fi

# ── 5. SSH Keys ────────────────────────────────────────────────────────────
echo ""
echo "━━━ [5/10] SSH Keys ─━━"
mkdir -p ~/.ssh
chmod 700 ~/.ssh

if [ -f "$REPO_DIR/ssh/id_ed25519" ]; then
    cp "$REPO_DIR/ssh/id_ed25519" ~/.ssh/id_ed25519
    chmod 600 ~/.ssh/id_ed25519
    echo "⚠️  SSH PRIVATE KEY restored (sensitive file!)"
fi
if [ -f "$REPO_DIR/ssh/id_ed25519.pub" ]; then
    cp "$REPO_DIR/ssh/id_ed25519.pub" ~/.ssh/id_ed25519.pub
    chmod 644 ~/.ssh/id_ed25519.pub
    echo "✅ SSH public key restored"
fi

# ── 6. FlowCore Toolkit ────────────────────────────────────────────────────
echo ""
echo "━━━ [6/10] FlowCore Toolkit ─━━"
if [ -d "$REPO_DIR/tools/flowcore" ]; then
    mkdir -p ~/flowcore
    cp -r "$REPO_DIR/tools/flowcore/"* ~/flowcore/ 2>/dev/null || true
    echo "✅ FlowCore toolkit restored to ~/flowcore/"
fi

# Standalone tools to ~/bounty_output
if [ -d "$REPO_DIR/tools" ]; then
    mkdir -p ~/bounty_output ~/airdrop_pipeline
    for f in ghost_creator.py ghost_tester.py income_pipeline.py farming_guide.py airdrop_monitor.py; do
        if [ -f "$REPO_DIR/tools/$f" ]; then
            cp "$REPO_DIR/tools/$f" ~/bounty_output/"$f" 2>/dev/null || true
        fi
    done
    # farming_guide and monitor go to airdrop_pipeline
    [ -f "$REPO_DIR/tools/farming_guide.py" ] && cp "$REPO_DIR/tools/farming_guide.py" ~/airdrop_pipeline/farming_guide.py
    [ -f "$REPO_DIR/tools/airdrop_monitor.py" ] && cp "$REPO_DIR/tools/airdrop_monitor.py" ~/airdrop_pipeline/monitor.py
    echo "✅ Standalone tools restored"
fi

# Data files
if [ -d "$REPO_DIR/data" ]; then
    mkdir -p ~/bounty_output
    cp "$REPO_DIR/data/"* ~/bounty_output/ 2>/dev/null || true
    echo "✅ Data files restored"
fi

# ── 7. Go 1.22.5 Installation ─────────────────────────────────────────────
echo ""
echo "━━━ [7/10] Go 1.22.5 Installation ─━━"
if ! command -v go &> /dev/null || ! go version | grep -q "go1.22.5"; then
    cd /tmp
    wget -q https://golang.org/dl/go1.22.5.linux-amd64.tar.gz
    rm -rf /usr/local/go
    tar -C /usr/local -xzf go1.22.5.linux-amd64.tar.gz
    rm go1.22.5.linux-amd64.tar.gz
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    export PATH=$PATH:/usr/local/go/bin
    echo "✅ Go 1.22.5 installed"
else
    echo "✅ Go $(go version | grep -oP 'go\d+\.\d+\.\d+') already installed"
fi

# ── 8. Security Tools (nuclei, subfinder, httpx) ───────────────────────────
echo ""
echo "━━━ [8/10] Security Tools ─━━"

# Install via go (projectdiscovery)
export PATH=$PATH:/usr/local/go/bin:~/go/bin

if ! command -v nuclei &> /dev/null; then
    echo "  Installing nuclei..."
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest 2>/dev/null || \
    wget -q https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_3.3.9_linux_amd64.zip -O /tmp/nuclei.zip && \
    unzip -q -o /tmp/nuclei.zip -d /tmp/nuclei && cp /tmp/nuclei/nuclei /usr/local/bin/ && rm -rf /tmp/nuclei* || \
    echo "  ⚠️ nuclei install skipped (try manually)"
fi

if ! command -v subfinder &> /dev/null; then
    echo "  Installing subfinder..."
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>/dev/null || \
    echo "  ⚠️ subfinder install skipped (try manually)"
fi

if ! command -v httpx &> /dev/null; then
    echo "  Installing httpx..."
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest 2>/dev/null || \
    echo "  ⚠️ httpx install skipped (try manually)"
fi

# ── 9. Playwright + Chromium ──────────────────────────────────────────────
echo ""
echo "━━━ [9/10] Playwright & Chromium ─━━"
pip3 install --upgrade pip
pip3 install playwright aiohttp aiohttp-socks pyyaml
python3 -m playwright install chromium 2>/dev/null || {
    echo "  ⚠️ playwright chromium install failed, trying with deps..."
    python3 -m playwright install --with-deps chromium 2>/dev/null || echo "  ⚠️ Install manually: playwright install --with-deps chromium"
}
echo "✅ Python dependencies installed"

# ── 10. Cron Jobs Restore & Permissions ───────────────────────────────────
echo ""
echo "━━━ [10/10] Cron Jobs & Permissions ─━━"

# Chmod +x everything
find ~/.hermes/scripts -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
find ~/.hermes/scripts -type f -name "*.py" -exec chmod +x {} \; 2>/dev/null || true
find ~/flowcore -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
find ~/flowcore -type f -name "*.py" -exec chmod +x {} \; 2>/dev/null || true
find ~/bounty_output -type f -name "*.py" -exec chmod +x {} \; 2>/dev/null || true
find ~/airdrop_pipeline -type f -name "*.py" -exec chmod +x {} \; 2>/dev/null || true

# Restore cron jobs via Hermes CLI
if command -v hermes &> /dev/null && [ -f ~/.hermes/cron/jobs.json ]; then
    echo "  Restoring Hermes cron jobs..."
    hermes cron import ~/.hermes/cron/jobs.json 2>/dev/null || echo "  ⚠️ Cron import failed (run manually: hermes cron import ~/.hermes/cron/jobs.json)"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ RESTORE COMPLETE                               ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🔑 IMPORTANT: Update API keys in ~/.hermes/config.yaml"
echo "   Look for 'YOUR_API_KEY_HERE' and replace with real keys"
echo ""
echo "📋 Quick verification:"
echo "   go version     → $(go version 2>/dev/null || echo 'check manually')"
echo "   python3 --version → $(python3 --version 2>/dev/null || echo 'check manually')"
echo ""
echo "🔄 Reboot recommended to apply all sysctl changes:"
echo "   sudo reboot"
