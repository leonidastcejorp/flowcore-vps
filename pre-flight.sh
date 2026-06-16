#!/bin/bash
# ============================================================================
# FlowCore VPS — Pre-Flight Check
# Checks system readiness before running full setup.
# Supports Ubuntu 22.04 AND 24.04
# Output: JSON {os, apt_locked, bg_updates, ram_mb, disk_mb, internet, status}
# ============================================================================

# ── OS Detection ─────────────────────────────────────────────────────────────
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_VERSION="$VERSION_ID"
        OS_CODENAME="$UBUNTU_CODENAME"
    elif command -v lsb_release &>/dev/null; then
        OS_VERSION=$(lsb_release -rs 2>/dev/null)
        OS_CODENAME=$(lsb_release -cs 2>/dev/null)
    else
        OS_VERSION="unknown"
        OS_CODENAME="unknown"
    fi
    echo "$OS_VERSION" "$OS_CODENAME"
}

# ── Apt Lock Check ──────────────────────────────────────────────────────────
check_apt_locked() {
    # Check multiple lock files
    for lock in /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock /var/cache/apt/archives/lock /var/lib/apt/lists/lock; do
        if [ -f "$lock" ]; then
            # Check if process actually holds the lock
            if fuser "$lock" &>/dev/null 2>&1; then
                echo "true"
                return
            fi
        fi
    done
    echo "false"
}

# ── Background Updates Check ────────────────────────────────────────────────
check_bg_updates() {
    # Check if unattended-upgrades or apt is running
    if pgrep -x "unattended-upgrade" &>/dev/null || \
       pgrep -x "apt-get" &>/dev/null || \
       pgrep -x "dpkg" &>/dev/null || \
       pgrep -x "apt" &>/dev/null; then
        echo "true"
    else
        echo "false"
    fi
}

# ── RAM Check ────────────────────────────────────────────────────────────────
check_ram() {
    if command -v free &>/dev/null; then
        free -m | awk '/^Mem:/ {print $7}'
    else
        echo "0"
    fi
}

# ── Disk Check ───────────────────────────────────────────────────────────────
check_disk() {
    if command -v df &>/dev/null; then
        df -m / | awk 'NR==2 {print $4}'
    else
        echo "0"
    fi
}

# ── Internet Check ───────────────────────────────────────────────────────────
check_internet() {
    if command -v ping &>/dev/null; then
        ping -c 1 -W 3 8.8.8.8 &>/dev/null && echo "true" || echo "false"
    else
        echo "false"
    fi
}

# ── Main ────────────────────────────────────────────────────────────────────
main() {
    read -r OS_VERSION OS_CODENAME <<< "$(detect_os)"
    APT_LOCKED=$(check_apt_locked)
    BG_UPDATES=$(check_bg_updates)
    RAM_MB=$(check_ram)
    DISK_MB=$(check_disk)
    INTERNET=$(check_internet)

    # Determine overall status
    STATUS="ready"
    if [ "$APT_LOCKED" = "true" ]; then
        STATUS="blocked"
    fi
    if [ "$BG_UPDATES" = "true" ]; then
        STATUS="blocked"
    fi
    if [ "$RAM_MB" != "0" ] && [ "$RAM_MB" -lt 256 ]; then
        STATUS="blocked"
    fi
    if [ "$DISK_MB" != "0" ] && [ "$DISK_MB" -lt 1024 ]; then
        STATUS="blocked"
    fi
    if [ "$INTERNET" = "false" ]; then
        STATUS="blocked"
    fi

    # Output JSON
    cat <<EOF
{
  "os": {"version": "$OS_VERSION", "codename": "$OS_CODENAME"},
  "apt_locked": $APT_LOCKED,
  "bg_updates": $BG_UPDATES,
  "ram_mb": $RAM_MB,
  "disk_mb": $DISK_MB,
  "internet": $INTERNET,
  "status": "$STATUS"
}
EOF
}

main
