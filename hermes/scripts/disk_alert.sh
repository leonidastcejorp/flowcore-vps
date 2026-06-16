#!/bin/bash
# 📀 DiskMon — ngasih tau kalo storage mau penuh atau swap bermasalah
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/lib/error_log.sh"

error_log_init "📀 DiskMon"
HAS_ISSUE=0

OUTPUT_HEADER=""
OUTPUT_SECTIONS=()

add_section() {
    local title="$1"
    OUTPUT_SECTIONS+=("$title")
    shift
    while [ $# -gt 0 ]; do
        OUTPUT_SECTIONS+=("$1")
        shift
    done
    OUTPUT_SECTIONS+=("")
}

# ── Cek disk ──
DISK_INFO=$(df / | awk 'NR==2 {print $5, $3, $2}' 2>/dev/null || true)
if [ -z "$DISK_INFO" ]; then
    error_log_ERROR "Gagal baca storage" "Perintah df -h error" "Cek manual: df -h"
    HAS_ISSUE=1
else
    DISK_PCT=$(echo "$DISK_INFO" | awk '{print $1}' | tr -d '%')
    DISK_USED=$(echo "$DISK_INFO" | awk '{print $2}')
    DISK_TOTAL=$(echo "$DISK_INFO" | awk '{print $3}')

    if ! [[ "$DISK_PCT" =~ ^[0-9]+$ ]]; then
        error_log_ERROR "Gagal baca angka" "Output: '$DISK_PCT'" "Cek df -h"
        HAS_ISSUE=1
    elif [ "$DISK_PCT" -gt 90 ]; then
        add_section "Disk" \
            "• Pemakaian: ${DISK_PCT}% (${DISK_USED}/${DISK_TOTAL}) — KRITIS!" \
            "• Dampak: Kurang dari 10% sisa!" \
            "• Saran: Hapus log: journalctl --vacuum-size=500M"
        error_log_CRITICAL "Disk mau penuh" "${DISK_PCT}% — sisa sedikit" "Hapus log & apt clean"
        HAS_ISSUE=1
    elif [ "$DISK_PCT" -gt 80 ]; then
        add_section "Disk" \
            "• Pemakaian: ${DISK_PCT}% (${DISK_USED}/${DISK_TOTAL})" \
            "• Saran: Pantau. apt clean kalo naik lagi"
        error_log_WARNING "Disk lumayan penuh" "${DISK_PCT}%" "Pantau"
        HAS_ISSUE=1
    else
        add_section "Disk" \
            "• Pemakaian: ${DISK_PCT}% (${DISK_USED}/${DISK_TOTAL})"
    fi
fi

# ── Cek swap ──
SWAP_OK=0
if swapon --show 2>/dev/null | grep -qE '/swapfile|/dev/zram'; then
    SWAP_OK=1
fi

if [ "$SWAP_OK" -eq 0 ]; then
    add_section "Swap" \
        "• Status: TIDAK AKTIF" \
        "• Dampak: VPS bisa OOM kalo RAM penuh" \
        "• Saran: Pasang swapfile 2GB"
    error_log_CRITICAL "Swap gak aktif" "Swapfile & ZRAM mati" "Pasang swapfile 2GB"
    HAS_ISSUE=1
else
    add_section "Swap" "• Status: Aktif ✅"
fi

# ── Cek ZRAM ──
if systemctl is-active --quiet zram-hermes.service 2>/dev/null; then
    ZRAM=$(zramctl --noheadings --raw --output=DISKSIZE,DATA 2>/dev/null | head -1 || true)
    if [ -n "$ZRAM" ]; then
        ZRAM_SIZE=$(echo "$ZRAM" | awk '{print $1}')
        ZRAM_USED=$(echo "$ZRAM" | awk '{print $2}')
        ZRAM_SIZE_MB=$(awk "BEGIN {printf \"%d\", $ZRAM_SIZE / 1048576}" 2>/dev/null || echo "?")
        ZRAM_USED_MB=$(awk "BEGIN {printf \"%d\", $ZRAM_USED / 1048576}" 2>/dev/null || echo "?")
        add_section "ZRAM" "• Size: ${ZRAM_SIZE_MB}MB (${ZRAM_USED_MB}MB terpakai)"
    fi
fi

# ── Output ──
if [ "$HAS_ISSUE" -eq 0 ]; then
    OUTPUT_HEADER="✅ 📀 DiskMon"
else
    OUTPUT_HEADER="🔴 📀 DiskMon"
fi

echo "$OUTPUT_HEADER"
echo ""
for s in "${OUTPUT_SECTIONS[@]}"; do
    echo "$s"
done

REPORT=$(error_log_report)
if [ -n "$REPORT" ]; then
    echo "$REPORT"
    echo ""
fi

echo "🕐 $(date '+%a %d %b %H:%M')"
error_log_persist
exit 0
