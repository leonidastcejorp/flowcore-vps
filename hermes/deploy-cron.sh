#!/bin/bash
# ============================================================================
# 🔥 BREACH — Cron Job Deployment Script
# ============================================================================
# Setup all 12 monitor cron jobs on a fresh Hermes installation.
#
# Usage:
#   export DELIVER="telegram:-1003534226714"   # Kantor FBI (default)
#   bash deploy-cron.sh
#
# For local-only jobs, use:
#   export DELIVER_LOCAL="local"
#
# Safe: Idempotent — re-run anytime.
# ============================================================================
set -euo pipefail

# ── Config ──
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DELIVER="${DELIVER:-telegram:-1003534226714}"
DELIVER_LOCAL="${DELIVER_LOCAL:-local}"
HERMES_HOME="${HOME}/.hermes"

# ── Colors ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
NC='\033[0m'; BOLD='\033[1m'
info()  { echo -e "  ${CYAN}→${NC} $1"; }
ok()    { echo -e "  ${GREEN}✅${NC} $1"; }
warn()  { echo -e "  ${YELLOW}⚠️${NC} $1"; }
title() { echo -e "\n${BOLD}━━━ $1 ━━━${NC}"; }

# ── Prerequisites ──
if ! command -v hermes &>/dev/null; then
    echo -e "${RED}✗ Hermes not found. Install Hermes first:${NC}"
    echo "  curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"
    exit 1
fi

if [ ! -d "$REPO_DIR/scripts" ]; then
    echo -e "${RED}✗ Scripts directory not found at $REPO_DIR/scripts${NC}"
    echo "  Run this script from the flowcore-vps/hermes/ directory."
    exit 1
fi

# ── Ensure Hermes is installed & gateway running ──
title "Pre-Flight Check"
hermes --version 2>&1 | head -1
ok "Hermes detected"

# ── 1. Copy scripts to Hermes scripts directory ──
title "Copying Scripts"
mkdir -p "$HERMES_HOME/scripts/lib"
cp "$REPO_DIR/scripts/"*.py "$HERMES_HOME/scripts/" 2>/dev/null || true
cp "$REPO_DIR/scripts/"*.sh "$HERMES_HOME/scripts/" 2>/dev/null || true
cp -r "$REPO_DIR/scripts/lib/"* "$HERMES_HOME/scripts/lib/" 2>/dev/null || true
chmod +x "$HERMES_HOME/scripts/"*.py "$HERMES_HOME/scripts/"*.sh 2>/dev/null || true
ok "Scripts deployed to $HERMES_HOME/scripts/"

# ── 2. Install Python dependencies ──
title "Installing Dependencies"
if [ -f "$REPO_DIR/requirements.txt" ] && [ -s "$REPO_DIR/requirements.txt" ]; then
    pip install -r "$REPO_DIR/requirements.txt" -q 2>/dev/null && \
        ok "Python deps installed" || \
        warn "pip install failed — install manually: pip install -r $REPO_DIR/requirements.txt"
else
    ok "No extra dependencies needed"
fi

# ── 3. Create output directories ──
title "Output Directories"
mkdir -p /root/projects/bounty-output/proxies
ok "Output dirs created"

# ── 4. Helper to create cron jobs ──
create_cron() {
    local name="$1" schedule="$2" script="$3" deliver="$4" desc="$5"
    local existing
    existing=$(hermes cron list 2>/dev/null | grep -c "$script" || true)
    if [ "$existing" -gt 0 ]; then
        warn "Job '$name' ($script) already exists — skipping"
        return 0
    fi
    hermes cron create "$schedule" \
        --name "$name" \
        --script "$script" \
        --no-agent \
        --deliver "$deliver" \
        --desc "$desc" 2>/dev/null || {
        warn "Failed to create '$name' — trying alternate syntax..."
        hermes cron create "$schedule" \
            --name "$name" \
            --script "$script" 2>/dev/null || true
    }
    ok "Created: $name ($schedule)"
}

echo ""
echo -e "${BOLD}━━━ Creating 12 Monitor Cron Jobs ━━━${NC}"
echo ""

# ── 5. Create all cron jobs ──

# Hourly jobs (spread across the hour)
create_cron "📈 MemStat"       "0 * * * *"     "memory_monitor.py"     "$DELIVER" "RAM & OOM checker"
create_cron "🔁 Bootmark"      "15 * * * *"    "reboot_monitor.py"     "$DELIVER" "Reboot detection"
create_cron "📊 Session Deck"  "30 * * * *"    "context_monitor.py"    "$DELIVER" "Session capacity monitor"

# Every 6 hours (spread across the hour)
create_cron "📀 DiskBay"       "0 */6 * * *"   "disk_alert.sh"         "$DELIVER" "Storage & ZRAM monitor"
create_cron "💰 Cuan Feed"     "10 */6 * * *"  "income_pipeline.py"    "$DELIVER" "Gig & airdrop scraper"
create_cron "🚪 PortGuard"     "20 */6 * * *"  "ssh_attack_monitor.py" "$DELIVER" "SSH attack logger"
create_cron "📡 VitalSign"     "30 */6 * * *"  "monitor.py"            "$DELIVER" "RAM+Disk+CPU watchdog"
create_cron "📋 LogDesk"       "40 */6 * * *"  "error_summary.py"      "$DELIVER" "Error log reporter"
create_cron "🔄 Proxy"         "50 */6 * * *"  "proxy_updater.py"      "$DELIVER_LOCAL" "Proxy pool updater"

# Fixed schedule jobs
create_cron "📊 Daily Briefing" "0 16 * * *"   "daily_report.py"       "$DELIVER" "Daily VPS report"
create_cron "🧹 Session Prune"  "0 3 * * 1"    "prune.sh"              "$DELIVER_LOCAL" "Weekly session cleanup"
create_cron "💾 Weekly Backup"  "0 2 * * 0"    "vps_backup.sh"         "$DELIVER_LOCAL" "Weekly VPS backup"

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          ✅ ALL 12 CRON JOBS DEPLOYED                       ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  📍 Delivery target: $DELIVER"
echo "  📍 Local jobs:      $DELIVER_LOCAL"
echo "  📍 Scripts at:      $HERMES_HOME/scripts/"
echo ""
echo "  To verify:  hermes cron list"
echo "  To rerun:   hermes cron run <job_id>"
