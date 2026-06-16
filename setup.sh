#!/bin/bash
# ============================================================================
# ═╗ ╦╦╔═╗╦═╗  ═╗ ╦╦╔═╗╦═╗  ┌─┐┬ ┬┌┐┌┌─┐┬┌─┐┌┐┌┌─┐┌─┐
# ╔╩╦╝║║ ╦╠╦╝  ╔╩╦╝║║ ╦╠╦╝  │  │ ││││├┤ ││ ││││└─┐├┤
# ╩ ╚═╩╚═╝╩╚═  ╩ ╚═╩╚═╝╩╚═  └─┘└─┘┘└┘└  ┴└─┘┘└┘└─┘└─┘
#
# 🔥 BREACH DEPLOYMENT — Full VPS Setup + Hardening + Farming Tools
# ============================================================================
# Usage:  bash setup.sh
# Tested: Ubuntu 24.04 LTS (fresh install)
# Safe:   Idempotent — re-run anytime without breaking things
# ============================================================================
set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────────
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/breach-deploy.log"
SSH_PORT="2222"
HERMES_VERSION="0.16.0"

# ── Colors ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
BOLD='\033[1m'; NC='\033[0m'; CHECK="✅"; WARN="⚠️"; SKIP="⏭️"

info()  { echo -e "  ${CYAN}→${NC} $1"; }
ok()    { echo -e "  ${CHECK} $1"; }
warn()  { echo -e "  ${WARN} $1"; }
skip()  { echo -e "  ${SKIP} $1"; }
title() { echo -e "\n${BOLD}━━━ $1 ━━━${NC}"; }

# ── Helpers ────────────────────────────────────────────────────────────────
is_installed() { command -v "$1" &>/dev/null; }
pkg_install() {
    local pkgs=()
    for pkg in "$@"; do
        dpkg -s "$pkg" &>/dev/null && skip "$pkg already installed" || pkgs+=("$pkg")
    done
    [ ${#pkgs[@]} -gt 0 ] && DEBIAN_FRONTEND=noninteractive apt install -y "${pkgs[@]}" || true
}

line() { echo "──────────────────────────────────────────────────────────────"; }

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                          PHASE 0: SYSTEM BASE                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝
phase_base() {
    title "PHASE 0: System Base"

    # ── 0.1 OS Check ──
    if [ ! -f /etc/os-release ] || ! grep -qi "ubuntu" /etc/os-release; then
        echo -e "${RED}✗ This script requires Ubuntu 24.04${NC}"
        exit 1
    fi
    ok "Ubuntu detected: $(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)"

    # ── 0.2 Update & Upgrade ──
    info "Updating package lists..."
    apt update -y
    apt upgrade -y
    ok "System updated"

    # ── 0.3 Base Packages ──
    title "Base Packages"
    pkg_install \
        git curl wget unzip gpg lsb-release ca-certificates \
        python3 python3-pip python3-venv \
        ufw fail2ban \
        auditd aide rkhunter lynis \
        unattended-upgrades \
        systemd-journal-remote \
        lsof \
        net-tools dnsutils \
        htop iotop \
        tmux

    # ── 0.4 DNS — Cloudflare + Google ──
    title "DNS Configuration"
    if ! grep -q "1.1.1.1" /etc/resolv.conf 2>/dev/null; then
        cat > /etc/resolv.conf << 'EOF'
nameserver 1.1.1.1
nameserver 8.8.8.8
EOF
        chattr +i /etc/resolv.conf 2>/dev/null || true
        ok "DNS set to 1.1.1.1 / 8.8.8.8 (immutable)"
    else
        skip "DNS already configured"
    fi

    # ── 0.5 Timezone ──
    timedatectl set-timezone Asia/Jakarta 2>/dev/null || true
    ok "Timezone: Asia/Jakarta"

    # ── 0.6 Python ──
    title "Python Environment"
    if [ ! -d /opt/breach-venv ]; then
        python3 -m venv /opt/breach-venv
        ok "Created /opt/breach-venv"
    fi
    source /opt/breach-venv/bin/activate
    pip install --quiet --upgrade pip
    # Farming & tool deps (excluding web3 which is heavy)
    pip install --quiet aiohttp aiohttp-socks pyyaml
    ok "Python base packages installed"
}

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                     PHASE 1: KERNEL HARDENING                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝
phase_kernel() {
    title "PHASE 1: Kernel Hardening"

    # ── 1.1 Swappiness ──
    if grep -q "vm.swappiness=10" /etc/sysctl.conf 2>/dev/null || [ -f /etc/sysctl.d/*swappiness* ]; then
        skip "swappiness already configured"
    else
        echo "vm.swappiness=10" >> /etc/sysctl.conf
        sysctl vm.swappiness=10
        ok "Swappiness set to 10"
    fi

    # ── 1.2 Performance Tuning (99-breacb.conf) ──
    if [ ! -f /etc/sysctl.d/99-breacb.conf ]; then
        cat > /etc/sysctl.d/99-breacb.conf << 'SYSCTL'
# 🔥 BREACH VPS — Kernel tuning
# TCP BBR congestion control
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr

# Network buffers
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728

# Connection tracking
net.netfilter.nf_conntrack_max = 1048576
net.ipv4.tcp_max_syn_backlog = 65536

# Security
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1
SYSCTL
        ok "Created 99-breacb.conf (BBR + network perf)"
    else
        skip "99-breacb.conf exists"
    fi

    # ── 1.3 Security Hardening (99-hardening.conf) ──
    if [ ! -f /etc/sysctl.d/99-hardening.conf ]; then
        cat > /etc/sysctl.d/99-hardening.conf << 'SYSCTL'
# 🔥 BREACH Hardening — Security sysctls
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 2
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv4.ip_forward = 0
kernel.exec-shield = 1
kernel.randomize_va_space = 2
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
kernel.perf_event_paranoid = 3
kernel.yama.ptrace_scope = 1
kernel.sysrq = 0
SYSCTL
        ok "Created 99-hardening.conf"
    else
        skip "99-hardening.conf exists"
    fi

    # ── 1.4 Hermes Optimizations (99-hermes-optimizations.conf) ──
    if [ ! -f /etc/sysctl.d/99-hermes-optimizations.conf ]; then
        cat > /etc/sysctl.d/99-hermes-optimizations.conf << 'SYSCTL'
# BREACH VPS — Hermes Optimizations
vm.dirty_ratio = 10
vm.dirty_background_ratio = 5
vm.vfs_cache_pressure = 500
vm.swappiness = 10
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_slow_start_after_idle = 0
net.core.somaxconn = 4096
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_intvl = 30
net.ipv4.tcp_keepalive_probes = 3
fs.inotify.max_user_watches = 65536
fs.inotify.max_user_instances = 1024
kernel.numa_balancing = 0
SYSCTL
        ok "Created 99-hermes-optimizations.conf"
    else
        skip "99-hermes-optimizations.conf exists"
    fi

    sysctl --system >/dev/null 2>&1
    ok "All sysctls applied"

    # ── 1.5 Kernel Module Blacklist ──
    if [ ! -f /etc/modprobe.d/blacklist-hardening.conf ]; then
        cat > /etc/modprobe.d/blacklist-hardening.conf << 'BLACKLIST'
# 🔥 BREACH Hardening — Blacklisted kernel modules
blacklist bluetooth
blacklist btusb
blacklist firewire-core
blacklist firewire-ohci
blacklist firewire-sbp2
blacklist pcmcia
blacklist pcmcia_core
blacklist yenta_socket
blacklist squashfs
blacklist vfat
blacklist hfs
blacklist hfsplus
blacklist jffs2
blacklist cramfs
blacklist freevxfs
blacklist udf
blacklist usb-storage
blacklist dccp
blacklist sctp
blacklist rds
blacklist tipc
BLACKLIST
        ok "Created module blacklist"
    else
        skip "module blacklist exists"
    fi
}

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                      PHASE 2: SSH HARDENING                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝
phase_ssh() {
    title "PHASE 2: SSH Hardening"

    # ── 2.1 SSH Directory ──
    mkdir -p /root/.ssh
    chmod 700 /root/.ssh

    # ── 2.2 SSH Key (auto-generate if missing) ──
    if [ ! -f /root/.ssh/authorized_keys ] || [ ! -s /root/.ssh/authorized_keys ]; then
        # Auto-generate keypair
        ssh-keygen -t ed25519 -f /root/.ssh/id_grace -N "" -C "grace-ku-sayang-$(date +%Y%m%d)" -q
        cp /root/.ssh/id_grace.pub /root/.ssh/authorized_keys
        chmod 600 /root/.ssh/id_grace
        chmod 644 /root/.ssh/id_grace.pub
        
        # Save private key in /root/.ssh/id_grace.export (user must retrieve it)
        # User should connect via VNC or provider console to grab it
        echo ""
        echo "╔══════════════════════════════════════════════════════════════════╗"
        echo "║  🔑 NEW SSH KEY GENERATED                                      ║"
        echo "╠══════════════════════════════════════════════════════════════════╣"
        echo "║  Private key saved to: /root/.ssh/id_grace                     ║"
        echo "║                                                                ║"
        echo "║  COPY THIS KEY TO YOUR DEVICE NOW or you will LOSE ACCESS:     ║"
        echo "╚══════════════════════════════════════════════════════════════════╝"
        echo ""
        cat /root/.ssh/id_grace
        echo ""
        echo "╔══════════════════════════════════════════════════════════════════╗"
        echo "║  Script will continue in 15 seconds...                         ║"
        echo "╚══════════════════════════════════════════════════════════════════╝"
        sleep 15
        ok "SSH key generated. Private key shown above — save it!"
    else
        skip "SSH authorized_keys already exists"
    fi

    chmod 600 /root/.ssh/authorized_keys 2>/dev/null || true

    # ── 2.3 SSH Server Config ──
    mkdir -p /etc/ssh/sshd_config.d

    cat > /etc/ssh/sshd_config.d/hardening.conf << SSHCONF
# 🔥 BREACH Hardening — key-only, port ${SSH_PORT}
Port ${SSH_PORT}
PubkeyAuthentication yes
PasswordAuthentication no
PermitRootLogin prohibit-password
AuthenticationMethods publickey
X11Forwarding no
MaxAuthTries 3
MaxSessions 5
ClientAliveInterval 300
ClientAliveCountMax 2
SSHCONF

    # Fix the main config
    sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config 2>/dev/null || true
    sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config 2>/dev/null || true
    sed -i 's/^#\?X11Forwarding.*/X11Forwarding no/' /etc/ssh/sshd_config 2>/dev/null || true
    sed -i 's/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config 2>/dev/null || true

    # Disable systemd socket activation (we use port override)
    systemctl disable --now ssh.socket 2>/dev/null || true

    systemctl restart sshd
    ok "SSH configured on port ${SSH_PORT}, key-only"
}

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                    PHASE 3: FIREWALL + FAIL2BAN                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝
phase_firewall() {
    title "PHASE 3: Firewall + Fail2Ban"

    # ── 3.1 UFW ──
    ufw --force reset 2>/dev/null || true
    ufw default deny incoming
    ufw default allow outgoing
    ufw limit ${SSH_PORT}/tcp
    ufw --force enable
    ok "UFW: default deny incoming, limit on port ${SSH_PORT}"

    # ── 3.2 Fail2Ban ──
    mkdir -p /etc/fail2ban/jail.d

    cat > /etc/fail2ban/jail.d/defaults-debian.conf << 'F2B'
[DEFAULT]
banaction = nftables
banaction_allports = nftables[type=allports]
backend = systemd
F2B

    cat > /etc/fail2ban/jail.d/sshd-port.conf << F2B
[sshd]
enabled       = true
port          = ${SSH_PORT}
logpath       = %(sshd_log)s
backend       = %(sshd_backend)s
banaction     = iptables-allports
maxretry      = 3
bantime       = 3600
findtime      = 600
F2B

    cat > /etc/fail2ban/jail.d/recidive.conf << 'F2B'
[recidive]
enabled     = true
logpath     = /var/log/fail2ban.log
banaction   = iptables-allports
maxretry    = 3
findtime    = 86400
bantime     = -1
F2B

    systemctl enable --now fail2ban
    sleep 2
    ok "Fail2Ban: sshd (port ${SSH_PORT}) + recidive (perma-ban)"
}

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                   PHASE 4: GEO-BLOCKING (IPSET)                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝
phase_geoip() {
    title "PHASE 4: Geo-Blocking (ipset)"

    if ! is_installed ipset; then
        pkg_install ipset
    fi

    # ── 4.1 Create ipset lists ──
    ipset list blacklist &>/dev/null || ipset create blacklist hash:net 2>/dev/null || true
    ipset list whitelist &>/dev/null || ipset create whitelist hash:net 2>/dev/null || true

    # ── 4.2 Download country blocks ──
    info "Downloading IP ranges for blocked countries (RU, CN, UZ, LT)..."
    BLOCKED_COUNTRIES="RU CN UZ LT"
    TEMP_BLOCK=$(mktemp)
    for cc in $BLOCKED_COUNTRIES; do
        if curl -sf "https://raw.githubusercontent.com/herrbischoff/country-ip-blocks/master/ipv4/${cc}.cidr" -o "/tmp/${cc}.cidr" 2>/dev/null; then
            cat "/tmp/${cc}.cidr" >> "$TEMP_BLOCK"
            rm -f "/tmp/${cc}.cidr"
        fi
    done

    if [ -s "$TEMP_BLOCK" ]; then
        TOTAL_BLOCKED=0
        while IFS= read -r cidr; do
            [ -z "$cidr" ] && continue
            ipset -q add blacklist "$cidr" && TOTAL_BLOCKED=$((TOTAL_BLOCKED + 1))
        done < "$TEMP_BLOCK"
        rm -f "$TEMP_BLOCK"
        ok "${TOTAL_BLOCKED} IP ranges blocked (RU/CN/UZ/LT)"
    else
        warn "Could not download country IP lists (no internet?). Skipping ipset block."
    fi

    # ── 4.3 Indonesian whitelist ──
    TEMP_WHITE=$(mktemp)
    info "Downloading Indonesian IP ranges for whitelist..."
    if curl -sf "https://raw.githubusercontent.com/herrbischoff/country-ip-blocks/master/ipv4/ID.cidr" -o /tmp/ID.cidr 2>/dev/null; then
        TOTAL_WHITE=0
        while IFS= read -r cidr; do
            [ -z "$cidr" ] && continue
            ipset -q add whitelist "$cidr" && TOTAL_WHITE=$((TOTAL_WHITE + 1))
        done < /tmp/ID.cidr
        rm -f /tmp/ID.cidr
        ok "${TOTAL_WHITE} Indonesian IP ranges whitelisted"
    else
        warn "Could not download ID whitelist"
    fi
    rm -f "$TEMP_WHITE"

    # ── 4.4 iptables rules for ipset ──
    # Insert blacklist DROP before UFW (position 1)
    if ! iptables -C INPUT -m set --match-set blacklist src -j DROP 2>/dev/null; then
        iptables -I INPUT 1 -m set --match-set blacklist src -j DROP
    fi
    # Insert whitelist ACCEPT after blacklist (position 2) - subject to fail2ban
    if ! iptables -C INPUT -m set --match-set whitelist src -j ACCEPT 2>/dev/null; then
        iptables -I INPUT 2 -m set --match-set whitelist src -j ACCEPT
    fi
    ok "iptables ipset rules active"

    # ── 4.5 ipset persistence ──
    mkdir -p /etc/ipset
    ipset save > /etc/ipset/ipset.rules 2>/dev/null || true

    # systemd unit for ipset restore on boot
    if [ ! -f /etc/systemd/system/ipset-persistent.service ]; then
        cat > /etc/systemd/system/ipset-persistent.service << 'SERVICE'
[Unit]
Description=ipset persistent restore
Before=ufw.service
DefaultDependencies=no

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/sbin/ipset restore -exist -file /etc/ipset/ipset.rules
ExecStop=/sbin/ipset save -file /etc/ipset/ipset.rules

[Install]
WantedBy=multi-user.target
SERVICE
        systemctl enable ipset-persistent
        ok "ipset persistence enabled"
    fi
}

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                    PHASE 5: DETECTION TOOLS                             ║
# ╚══════════════════════════════════════════════════════════════════════════╝
phase_detection() {
    title "PHASE 5: Detection Tools"

    # ── 5.1 Auditd ──
    cat > /etc/audit/rules.d/breach.rules << 'AUDIT'
# 🔥 BREACH — Critical file monitoring
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/sudoers -p wa -k sudoers
-w /etc/ssh/sshd_config -p wa -k sshd_config
-w /etc/ssh/sshd_config.d/ -p wa -k sshd_config
-w /root/.ssh/ -p wa -k ssh_changes
-w /root/.hermes/ -p wa -k hermes_changes
-a always,exit -S execve -F euid=0 -k root_exec

# Increase buffer, failure to syslog
-b 8192
--backlog_wait_time 60000
-f 1
AUDIT
    systemctl enable --now auditd 2>/dev/null || true
    auditctl -R /etc/audit/rules.d/breach.rules 2>/dev/null || true
    ok "Auditd: monitoring critical files"

    # ── 5.2 AIDE ──
    if [ ! -f /var/lib/aide/aide.db ]; then
        info "Initializing AIDE (first run requires compilation, may take a minute)..."
        aideinit 2>&1 | tail -1 || true
        cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db 2>/dev/null || true
    fi
    # AIDE daily check is installed by the package in cron.daily
    if [ -f /etc/cron.daily/dailyaidecheck ]; then
        ok "AIDE: initialized + daily check active"
    else
        warn "AIDE daily check cron not found"
    fi

    # ── 5.3 RKHunter ──
    if [ -f /etc/default/rkhunter ]; then
        sed -i 's/^CRON_DAILY_RUN=.*/CRON_DAILY_RUN="true"/' /etc/default/rkhunter 2>/dev/null || true
        rkhunter --propupd 2>&1 | tail -2 || true
        ok "RKHunter: daily cron active"
    fi

    # ── 5.4 Lynis — already installed as package ──
    ok "Lynis: installed (run manually: lynis audit system)"
}

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                PHASE 6: AUTO UPDATES + JOURNALD                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝
phase_maintenance() {
    title "PHASE 6: Maintenance"

    # ── 6.1 Unattended Upgrades ──
    cat > /etc/apt/apt.conf.d/20auto-upgrades << 'APT'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
APT

    cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'APT'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::OnlyOnACPower "false";
APT
    ok "Unattended upgrades: security only, no auto-reboot"

    # ── 6.2 Journald ──
    mkdir -p /etc/systemd/journald.conf.d
    cat > /etc/systemd/journald.conf.d/breach.conf << 'JOURNAL'
[Journal]
Compress=yes
SystemMaxUse=200M
MaxFileSec=1month
JOURNAL
    systemctl restart systemd-journald
    ok "Journald: 200MB max, compressed"

    # ── 6.3 Swap (if needed) ──
    if [ "$(free -m | awk '/Swap:/{print $2}')" -lt 2000 ]; then
        if [ ! -f /swapfile ]; then
            fallocate -l 2G /swapfile 2>/dev/null || dd if=/dev/zero of=/swapfile bs=1M count=2048 status=none
            chmod 600 /swapfile
            mkswap /swapfile >/dev/null 2>&1
            swapon /swapfile >/dev/null 2>&1
            if ! grep -q swapfile /etc/fstab; then
                echo "/swapfile none swap sw 0 0" >> /etc/fstab
            fi
            ok "2GB swapfile created"
        fi
    else
        skip "Swap sufficient ($(free -m | awk '/Swap:/{print $2}')MB)"
    fi
}

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                PHASE 7: FARMING TOOLS + RUNTIME                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝
phase_tools() {
    title "PHASE 7: Farming Tools & Runtimes"

    # ── 7.1 Go ──
    if ! is_installed go || ! go version | grep -q "go1.22"; then
        info "Installing Go 1.22..."
        cd /tmp
        wget -q "https://go.dev/dl/go1.22.5.linux-amd64.tar.gz" -O go.tar.gz
        rm -rf /usr/local/go
        tar -C /usr/local -xzf go.tar.gz
        rm -f go.tar.gz
        export PATH="$PATH:/usr/local/go/bin"
        echo 'export PATH=$PATH:/usr/local/go/bin' >> /root/.bashrc
        ok "Go 1.22.5 installed"
    else
        skip "Go $(go version | grep -oP 'go\S+') already installed"
    fi

    # ── 7.2 Security/Bug Bounty Tools ──
    export GOPATH="$HOME/go"
    export PATH="$PATH:/usr/local/go/bin:$GOPATH/bin"
    mkdir -p "$GOPATH/bin"

    if ! is_installed nuclei; then
        info "Installing nuclei..."
        go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest 2>/dev/null || warn "nuclei install failed"
    else
        skip "nuclei installed"
    fi

    if ! is_installed subfinder; then
        info "Installing subfinder..."
        go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>/dev/null || warn "subfinder install failed"
    else
        skip "subfinder installed"
    fi

    if ! is_installed httpx; then
        info "Installing httpx..."
        go install github.com/projectdiscovery/httpx/cmd/httpx@latest 2>/dev/null || warn "httpx install failed"
    else
        skip "httpx installed"
    fi

    # ── 7.3 Symlinks in ~/tools/bin ──
    mkdir -p ~/tools/bin
    for tool in nuclei subfinder httpx; do
        if [ -f "$GOPATH/bin/$tool" ] && [ ! -L ~/tools/bin/$tool ]; then
            ln -sf "$GOPATH/bin/$tool" ~/tools/bin/$tool
        fi
    done
    ok "Bug bounty tools: nuclei, subfinder, httpx"

    # ── 7.4 Node.js + PM2 ──
    if ! is_installed node || ! node --version | grep -q "v22"; then
        info "Installing Node.js 22..."
        # Use n-install for lightweight version management
        wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash 2>/dev/null || true
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" 2>/dev/null || true
        nvm install 22 2>/dev/null || {
            # Fallback: use nodesource
            curl -fsSL https://deb.nodesource.com/setup_22.x | bash - 2>/dev/null
            apt install -y nodejs 2>/dev/null
        }
        ok "Node.js $(node --version) installed"
    else
        skip "Node.js $(node --version) already installed"
    fi

    if ! is_installed pm2; then
        npm install -g pm2 yarn 2>/dev/null || warn "pm2/yarn install failed"
        ok "PM2 + Yarn installed"
    else
        skip "PM2 already installed"
    fi

    # ── 7.5 Playwright + Chromium (for browser automation) ──
    if ! python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
        info "Installing Playwright + Chromium..."
        pip3 install playwright 2>/dev/null
        python3 -m playwright install --with-deps chromium 2>/dev/null || \
            python3 -m playwright install chromium 2>/dev/null || \
            warn "Playwright Chromium install had issues (run manually)"
        ok "Playwright + Chromium installed"
    else
        skip "Playwright already installed"
    fi

    # ── 7.6 Web3 (for testnet farming) ──
    if ! python3 -c "import web3" 2>/dev/null; then
        pip3 install web3 2>/dev/null || true
        ok "web3.py installed"
    else
        skip "web3.py already installed"
    fi

    # ── 7.7 Create project directories ──
    mkdir -p ~/projects/{airdrop-pipeline,bounty-output,flowcore}
    mkdir -p ~/projects/bounty-output/proxies
    ok "Project directories created"

    # ── 7.8 Copy project files from repo (if available) ──
    if [ -d "$REPO_DIR/tools" ]; then
        cp "$REPO_DIR/tools/"*.py ~/projects/airdrop-pipeline/ 2>/dev/null || true
        ok "Airdrop pipeline scripts copied"
    fi
    if [ -d "$REPO_DIR/data" ]; then
        cp "$REPO_DIR/data/"* ~/projects/bounty-output/ 2>/dev/null || true
        ok "Data files copied"
    fi
}

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                     PHASE 8: HERMES AGENT                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝
phase_hermes() {
    title "PHASE 8: Hermes Agent"

    # ── 8.1 Install Hermes ──
    if ! is_installed hermes; then
        info "Installing Hermes Agent v${HERMES_VERSION}..."
        bash <(curl -fsSL https://hermes-agent.nousresearch.com/install.sh) 2>&1 | tail -3
        ok "Hermes Agent installed"
    else
        skip "Hermes $(hermes --version 2>&1 | head -1) already installed"
    fi

    # ── 8.2 Create hermes user (if not exists) ──
    if ! id hermes &>/dev/null; then
        useradd -r -s /usr/sbin/nologin -m -d /home/hermes hermes
        ok "User 'hermes' created"
    else
        skip "User 'hermes' already exists"
    fi

    # ── 8.3 Copy configs ──
    mkdir -p /home/hermes/.hermes /home/hermes/.ssh

    if [ -f "$REPO_DIR/hermes/config.yaml" ]; then
        cp "$REPO_DIR/hermes/config.yaml" /home/hermes/.hermes/config.yaml
        chown hermes:hermes /home/hermes/.hermes/config.yaml
        chmod 600 /home/hermes/.hermes/config.yaml
        echo ""
        echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${YELLOW}║  ⚠️  UPDATE YOUR API KEYS in /home/hermes/.hermes/config.yaml ║${NC}"
        echo -e "${YELLOW}║  Look for 'api_key' fields and replace with real keys        ║${NC}"
        echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════╝${NC}"
        ok "Hermes config copied (API keys need manual update)"
    else
        warn "No hermes config found in repo. Create /home/hermes/.hermes/config.yaml manually"
    fi

    if [ -f "$REPO_DIR/hermes/SOUL.md" ]; then
        cp "$REPO_DIR/hermes/SOUL.md" /home/hermes/.hermes/SOUL.md
        chown hermes:hermes /home/hermes/.hermes/SOUL.md
        ok "SOUL.md copied"
    fi

    # Copy scripts
    if [ -d "$REPO_DIR/hermes/scripts" ]; then
        mkdir -p /home/hermes/.hermes/scripts
        cp "$REPO_DIR/hermes/scripts/"*.py /home/hermes/.hermes/scripts/ 2>/dev/null || true
        cp "$REPO_DIR/hermes/scripts/"*.sh /home/hermes/.hermes/scripts/ 2>/dev/null || true
        chown -R hermes:hermes /home/hermes/.hermes/scripts
        find /home/hermes/.hermes/scripts -type f -exec chmod +x {} \; 2>/dev/null || true
        ok "Hermes scripts copied"
    fi

    # Copy lib/ (error_log shared library)
    if [ -d "$REPO_DIR/hermes/scripts/lib" ]; then
        mkdir -p /home/hermes/.hermes/scripts/lib
        cp -r "$REPO_DIR/hermes/scripts/lib/"* /home/hermes/.hermes/scripts/lib/ 2>/dev/null || true
        chown -R hermes:hermes /home/hermes/.hermes/scripts/lib
        ok "Hermes script lib copied"
    fi

    # Install Python dependencies
    if [ -f "$REPO_DIR/hermes/requirements.txt" ] && [ -s "$REPO_DIR/hermes/requirements.txt" ]; then
        info "Installing Hermes Python deps..."
        pip install -r "$REPO_DIR/hermes/requirements.txt" -q 2>/dev/null && \
            ok "Python deps installed" || \
            warn "pip install failed — run manually: pip install -r $REPO_DIR/hermes/requirements.txt"
    fi

    # Copy cron jobs
    if [ -f "$REPO_DIR/hermes/cron/jobs.json" ]; then
        mkdir -p /home/hermes/.hermes/cron
        cp "$REPO_DIR/hermes/cron/jobs.json" /home/hermes/.hermes/cron/jobs.json
        chown -R hermes:hermes /home/hermes/.hermes/cron
        ok "Cron jobs copied"
    fi

    # Copy plugins
    if [ -d "$REPO_DIR/hermes/plugins" ]; then
        mkdir -p /home/hermes/.hermes/plugins
        cp -r "$REPO_DIR/hermes/plugins/"* /home/hermes/.hermes/plugins/ 2>/dev/null || true
        chown -R hermes:hermes /home/hermes/.hermes/plugins
        ok "Hermes plugins copied"
    fi

    # ── 8.4 systemd service ──
    cat > /etc/systemd/system/hermes.service << 'SERVICE'
[Unit]
Description=Hermes Agent — grace-ku-sayang
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=hermes
Group=hermes
WorkingDirectory=/home/hermes
ExecStart=/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main gateway run
Restart=on-failure
RestartSec=10

# 🔐 Sandbox
ProtectSystem=full
PrivateTmp=yes
NoNewPrivileges=yes
CapabilityBoundingSet=
ProtectClock=yes
ProtectKernelModules=yes
ProtectKernelTunables=yes
ProtectProc=invisible
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
RestrictRealtime=yes
SystemCallArchitectures=native

[Install]
WantedBy=multi-user.target
SERVICE

    systemctl daemon-reload
    systemctl enable hermes
    ok "Hermes systemd service created (not started yet — update config first)"

    # ── 8.5 Output directories ──
    mkdir -p /root/projects/bounty-output/proxies
    ok "Monitor output directories created"
}

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                     PHASE 9: FINALIZATION                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝
phase_final() {
    title "PHASE 9: Finalization"

    # ── 9.1 Bashrc tweaks ──
    if ! grep -q "breach-venv" /root/.bashrc 2>/dev/null; then
        cat >> /root/.bashrc << 'BASHRC'

# 🔥 BREACH — Aliases & Path
alias ll='ls -lah'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ..2='cd ../..'
alias ..3='cd ../../..'
alias df='df -h'
alias du='du -h --max-depth=1'
alias free='free -h'
alias ip='ip -c'
alias ports='ss -tlnp'
alias psg='ps aux | grep'
alias myip='curl -sf ifconfig.me'
alias ufw-status='ufw status verbose'
alias f2b-status='fail2ban-client status'
alias lynis-run='lynis audit system'
alias aide-check='aide --check'
alias aide-update='aideinit && cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db'
source /opt/breach-venv/bin/activate
BASHRC
        ok "Bash aliases added"
    fi

    # ── 9.2 MOTD — System Info ──
    cat > /etc/update-motd.d/99-breach << 'MOTD'
#!/bin/bash
echo ""
echo -e "\e[1;31m  🔥 BREACH VPS \e[0m— \e[1;37mgrace-ku-sayang\e[0m"
echo -e "\e[90m  $(date '+%A, %d %B %Y  %H:%M:%S WIB')\e[0m"
echo ""
MOTD
    chmod +x /etc/update-motd.d/99-breach
    ok "MOTD set"

    # ── 9.3 Cleanup ──
    apt autoremove --purge -y 2>/dev/null || true
    apt autoclean -y 2>/dev/null || true
    ok "System cleaned"

    # ── 9.4 Summary ──
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║        ✅ BREACH DEPLOYMENT COMPLETE                        ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BOLD}📋 What's installed:${NC}"
    echo "  ┌─────────────────────────────────────────────────────────┐"
    echo "  │ 🔒 SSH:       port ${SSH_PORT}, key-only                         │"
    echo "  │ 🛡️  UFW:       limit ${SSH_PORT}, default deny                     │"
    echo "  │ ⛔ fail2ban:   sshd + recidive (perma-ban)               │"
    echo "  │ 🌍 Geo-block:  RU/CN/UZ/LT blocked, ID whitelisted      │"
    echo "  │ 🔍 Auditd:     critical file monitoring                  │"
    echo "  │ 📊 AIDE:       daily integrity check                     │"
    echo "  │ 🕵️  RKHunter:   daily rootkit scan                       │"
    echo "  │ ⚡ Lynis:      system auditor (manual: lynis audit)      │"
    echo "  │ 🔄 Updates:    security auto-upgrades                    │"
    echo "  │ 🖥️  Go:        1.22.5 + nuclei/subfinder/httpx           │"
    echo "  │ 📦 Node:      v22 + PM2 + Yarn                          │"
    echo "  │ 🎭 Playwright: Chromium browser automation               │"
    echo "  │ 🧪 web3.py:   testnet farming ready                      │"
    echo "  │ 🤖 Hermes:    isolated user, systemd sandboxed           │"
    echo "  └─────────────────────────────────────────────────────────┘"
    echo ""
    echo -e "  ${YELLOW}⚠️  NEXT STEPS:${NC}"
    echo "  1. Update API keys in /home/hermes/.hermes/config.yaml"
    echo "  2. Deploy cron monitors:"
    echo "     cd ~/projects/flowcore-vps/hermes && bash deploy-cron.sh"
    echo "  3. If IP changed, update Telegram webhook"
    echo "  4. Reboot recommended to apply all changes:"
    echo "     sudo reboot"
    echo ""
    echo -e "  ${BOLD}🔥 BREACH — deployed with zero-fucks attitude${NC}"
    echo ""
}

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                          MAIN EXECUTION                                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# Root check
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}✗ This script must be run as root${NC}"
    exit 1
fi

# Log everything
exec > >(tee -ia "$LOG_FILE") 2>&1

echo ""
echo -e "${RED}╔══════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║                              🔥 BREACH                                   ║${NC}"
echo -e "${RED}║                    Full VPS Deployment — grace-ku-sayang                  ║${NC}"
echo -e "${RED}║                    Ubuntu 24.04 · Idempotent                              ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect existing state
if [ -f /var/log/breach-deploy.log ] && grep -q "BREACH DEPLOYMENT COMPLETE" /var/log/breach-deploy.log 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Existing deployment detected. Running in idempotent mode.${NC}"
    echo -e "${YELLOW}   Existing SSH keys and configs will be preserved.${NC}"
    echo ""
fi

phase_base
phase_kernel
phase_ssh
phase_firewall
phase_geoip
phase_detection
phase_maintenance
phase_tools
phase_hermes
phase_final

echo ""
echo -e "${GREEN}🔥 BREACH — deployment complete at $(date)${NC}"
