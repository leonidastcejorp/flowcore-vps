#!/bin/bash
# 📀 Disk Monitor — ngasih tau storage mau penuh / swap bermasalah
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/error_log.sh"

error_log_init "📀 DiskBay"
HAS_ISSUE=0
OUTPUT=()
TABLE_ROWS=()

# ── Cek disk ──
DISK_INFO=$(df -h / | awk 'NR==2 {print $5, $3, $2}' 2>/dev/null || true)
if [ -z "$DISK_INFO" ]; then
    error_log_ERROR "Storage error" "df -h gagal" "Cek manual: df -h"
    HAS_ISSUE=1
else
    DISK_PCT=$(echo "$DISK_INFO" | awk '{print $1}' | tr -d '%')
    DISK_USED=$(echo "$DISK_INFO" | awk '{print $2}')
    DISK_TOTAL=$(echo "$DISK_INFO" | awk '{print $3}')

    if ! [[ "$DISK_PCT" =~ ^[0-9]+$ ]]; then
        error_log_ERROR "Gagal baca angka disk" "Output: $DISK_PCT" "Cek df -h"
        HAS_ISSUE=1
    elif [ "$DISK_PCT" -gt 90 ]; then
        OUTPUT+=("💀 **Storage mau penuh!** ${DISK_PCT}% (${DISK_USED}/${DISK_TOTAL})")
        OUTPUT+=("   Sisa kurang dari 10% — segera bersihin!")
        OUTPUT+=("   → Hapus log: \`journalctl --vacuum-size=500M\`")
        error_log_CRITICAL "Disk mau penuh" "${DISK_PCT}%" "Bersihin: journalctl --vacuum-size=500M"
        HAS_ISSUE=1
    elif [ "$DISK_PCT" -gt 80 ]; then
        OUTPUT+=("🟡 **Disk mulai penuh** ${DISK_PCT}% (${DISK_USED}/${DISK_TOTAL})")
        OUTPUT+=("   → Pantau. Kalo naik, bersihin: \`apt clean\`")
        error_log_WARNING "Disk mulai penuh" "${DISK_PCT}%" "apt clean kalo naik"
        HAS_ISSUE=1
    else
        TABLE_ROWS+=("| Disk | ${DISK_PCT}% (${DISK_USED}/${DISK_TOTAL}) |")
    fi
fi

# ── Cek swap ──
SWAP_OK=0
if swapon --show 2>/dev/null | grep -qE '/swapfile|/dev/zram'; then
    SWAP_OK=1
fi

if [ "$SWAP_OK" -eq 0 ]; then
    OUTPUT+=("💀 **Swap gak aktif!**")
    OUTPUT+=("   VPS bisa kehabisan memory kalo RAM penuh tanpa cadangan swap")
    OUTPUT+=("   → Mau gua pasangin swapfile 2GB?")
    error_log_CRITICAL "Swap mati" "Swapfile & ZRAM gak aktif" "Pasang swapfile 2GB"
    HAS_ISSUE=1
else
    TABLE_ROWS+=("| Swap | Aktif ✅ |")
fi

# ── Cek ZRAM ──
if systemctl is-active --quiet zram-hermes.service 2>/dev/null; then
    ZRAM=$(zramctl --noheadings --raw --output=DISKSIZE,DATA 2>/dev/null | head -1 || true)
    if [ -n "$ZRAM" ]; then
        ZRAM_SIZE=$(echo "$ZRAM" | awk '{print $1}')
        ZRAM_USED=$(echo "$ZRAM" | awk '{print $2}')
        ZRAM_SIZE_MB=$(awk "BEGIN {printf \"%d\", $ZRAM_SIZE / 1048576}" 2>/dev/null || echo "?")
        ZRAM_USED_MB=$(awk "BEGIN {printf \"%d\", $ZRAM_USED / 1048576}" 2>/dev/null || echo "?")
        TABLE_ROWS+=("| ZRAM | ${ZRAM_SIZE_MB}MB (${ZRAM_USED_MB}MB terpakai) |")
    fi
fi

# ── OUTPUT ──
if [ "$HAS_ISSUE" -eq 0 ] && [ ${#TABLE_ROWS[@]} -gt 0 ]; then
    echo "✅ **📀 DiskBay**"
    echo ""
    echo "| Komponen | Status |"
    echo "|----------|--------|"
    for row in "${TABLE_ROWS[@]}"; do echo "$row"; done
    echo ""
    echo "🕐 $(date '+%a %d %b %H:%M')"
    error_log_persist
    exit 0
fi

# Ada issue — tampilin alert dulu
for line in "${OUTPUT[@]}"; do echo "$line"; done

if [ ${#TABLE_ROWS[@]} -gt 0 ]; then
    echo ""
    echo "| Komponen | Status |"
    echo "|----------|--------|"
    for row in "${TABLE_ROWS[@]}"; do echo "$row"; done
fi

error_log_persist
exit 0
