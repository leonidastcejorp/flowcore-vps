#!/usr/bin/env bash
# =============================================================================
# deploy-cron.sh — Deploy all 12 Hermes cron jobs for Flowcore VPS
# =============================================================================
# Idempotent: tracks deployed cron job IDs in ~/.hermes/.deployed_crons.
# Run this script multiple times safely — already-deployed jobs are skipped.
# =============================================================================
set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────────
CRON_STATE_FILE="$HOME/.hermes/.deployed_crons"
TELEGRAM_GROUP="-1003534226714"
TELEGRAM_USER="5695981991"

# ── Color output ───────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; }
info() { echo -e "  ${CYAN}→${NC} $1"; }

# ── Pre-flight checks ──────────────────────────────────────────────────────
if ! command -v hermes &>/dev/null; then
    echo -e "${RED}ERROR: Hermes CLI not found. Install it first:${NC}"
    echo "  curl -fsSL https://hermes-agent.nousresearch.com/install.sh | sh"
    exit 1
fi

HERMES_VERSION=$(hermes --version 2>/dev/null || hermes -v 2>/dev/null || echo "unknown")
echo -e "${CYAN}Hermes Agent:${NC} $HERMES_VERSION"
echo ""

# ── Initialize state file ──────────────────────────────────────────────────
mkdir -p "$(dirname "$CRON_STATE_FILE")"
touch "$CRON_STATE_FILE"

# ── Helper: deploy a single cron job ───────────────────────────────────────
# Usage: deploy_cron_job "SCHEDULE" "NAME" "SCRIPT" ["deliver"|"local"] [extra_args...]
deploy_cron_job() {
    local schedule="$1"
    local name="$2"
    local script="$3"
    local target="${4:-telegram}"
    shift 4
    local extra_args=("$@")

    # Build a unique lookup key from schedule + name
    local lookup_key="$(echo "$schedule" | tr -s ' ')||$name"

    # Check if already deployed
    if grep -Fxq "$lookup_key" "$CRON_STATE_FILE" 2>/dev/null; then
        warn "Already deployed — skipping: $name"
        return 0
    fi

    info "Deploying: $name"

    # Build the deliver argument
    local deliver_arg=""
    if [ "$target" = "local" ]; then
        deliver_arg="--deliver local"
    else
        deliver_arg="--deliver \"telegram:$TELEGRAM_GROUP\""
    fi

    # Build command
    local cmd=("hermes" "cron" "create" "$schedule")
    cmd+=("--name" "$name")
    cmd+=("--script" "$script")
    if [ "$target" != "local" ]; then
        cmd+=("--deliver" "telegram:$TELEGRAM_GROUP")
    fi
    # Add no-agent and repeat 0 for script-based jobs
    if [[ "$script" == *.sh ]]; then
        # Shell scripts — use no-agent
        cmd+=("--no-agent")
        cmd+=("--repeat" "0")
    elif [[ "$script" == *.py ]]; then
        # Python scripts — use no-agent
        cmd+=("--no-agent")
        cmd+=("--repeat" "0")
    else
        cmd+=("--repeat" "0")
    fi
    # Append any extra args
    if [ ${#extra_args[@]} -gt 0 ]; then
        cmd+=("${extra_args[@]}")
    fi

    # Run the command
    if "${cmd[@]}" 2>&1; then
        echo "$lookup_key" >> "$CRON_STATE_FILE"
        ok "Deployed: $name"
        return 0
    else
        local exit_code=$?
        # Check if it failed because job already exists (duplicate detection)
        fail "Failed (exit $exit_code): $name"
        return $exit_code
    fi
}

# ── Summary counters ───────────────────────────────────────────────────────
TOTAL=12
SUCCESS=0
FAILED=0
SKIPPED=0

# Helper to run and count
run_job() {
    if deploy_cron_job "$@"; then
        SUCCESS=$((SUCCESS + 1))
    else
        local rc=$?
        if [ $rc -eq 0 ]; then
            SKIPPED=$((SKIPPED + 1))
        else
            FAILED=$((FAILED + 1))
        fi
    fi
}

# ── Deploy all 12 cron jobs ────────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Deploying $TOTAL Hermes Cron Jobs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. 🚨 FBI Watchdog
run_job "every 360m" "🚨 FBI Watchdog" "monitor.py" "telegram"

# 2. 📊 FBI Daily Briefing
run_job "0 16 * * *" "📊 FBI Daily Briefing" "daily_report.py" "telegram"

# 3. 🧹 Hermes Session Prune
run_job "0 3 * * 1" "🧹 Hermes Session Prune" "prune.sh" "local"

# 4. 💰 Income Pipeline Monitor
run_job "every 360m" "💰 Income Pipeline Monitor" "income_pipeline.py" "telegram"

# 5. 🔁 Proxy Auto-Updater
run_job "every 360m" "🔁 Proxy Auto-Updater" "proxy_updater.py" "local"

# 6. 📦 VPS Weekly Backup
run_job "0 2 * * 0" "📦 VPS Weekly Backup" "vps_backup.sh" "local"

# 7. 💾 Disk Usage Watchdog
run_job "every 360m" "💾 Disk Usage Watchdog" "disk_alert.sh" "telegram"

# 8. 📈 Context Monitor
run_job "every 60m" "📈 Context Monitor" "context_monitor.py" "telegram"

# 9. 🚪 SSH Attack Monitor
run_job "every 360m" "🚪 SSH Attack Monitor" "ssh_attack_monitor.py" "telegram"

# 10. 🔁 Reboot Monitor
run_job "every 15m" "🔁 Reboot Monitor" "reboot_monitor.py" "telegram"

# 11. 📈 Memory Pressure Monitor
run_job "every 60m" "📈 Memory Pressure Monitor" "memory_monitor.py" "telegram"

# 12. 📋 Error Log Summary
run_job "every 360m" "📋 Error Log Summary" "error_summary.py" "telegram"

# ── Summary ────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Deployment Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${GREEN}Success:${NC}  $SUCCESS / $TOTAL"
echo -e "  ${YELLOW}Skipped:${NC}  $SKIPPED"
echo -e "  ${RED}Failed:${NC}   $FAILED"
echo ""
echo "  State file: $CRON_STATE_FILE"
echo ""

if [ "$FAILED" -gt 0 ]; then
    echo -e "${YELLOW}ℹ Some jobs failed. You can re-run this script to retry.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ All cron jobs deployed successfully.${NC}"
fi
