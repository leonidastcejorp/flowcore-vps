#!/bin/bash
set -euo pipefail

# ── Config ──────────────────────────────────────────────────────────────────
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
HERMES_SRC="/root/.hermes"
PROJECTS_SRC="/root/projects"
MAX_BACKUPS=5

# ── Exclusions (directories under /root/.hermes to skip) ───────────────────
EXCLUDE=(
    --exclude="cache"
    --exclude="sessions"
    --exclude="audio_cache"
    --exclude="image_cache"
    --exclude="node"
    --exclude="venv"
)

# ── Ensure backup directory exists ──────────────────────────────────────────
mkdir -p "$BACKUP_DIR"

# ── Create backups ──────────────────────────────────────────────────────────
HERMES_ARCHIVE="$BACKUP_DIR/hermes_$DATE.tar.gz"
PROJECTS_ARCHIVE="$BACKUP_DIR/projects_$DATE.tar.gz"

echo "=== Bikin backup: $HERMES_ARCHIVE ==="
tar -czf "$HERMES_ARCHIVE" "${EXCLUDE[@]}" -C / root/.hermes || {
    rc=$?
    # "file changed" warning still exits 1 — it's benign, ignore it
    if tar --version 2>/dev/null | grep -q '(GNU tar)'; then
        # GNU tar: 1 means some files changed during read; 2+ is real error
        [ "$rc" -gt 1 ] && exit "$rc"
    else
        exit "$rc"
    fi
}

echo "=== Bikin backup: $PROJECTS_ARCHIVE ==="
tar -czf "$PROJECTS_ARCHIVE" -C / root/projects || {
    rc=$?
    if tar --version 2>/dev/null | grep -q '(GNU tar)'; then
        [ "$rc" -gt 1 ] && exit "$rc"
    else
        exit "$rc"
    fi
}

# ── Prune old backups (keep only last MAX_BACKUPS per prefix) ──────────────
echo "=== Hapus backup lama (sisain $MAX_BACKUPS terakhir) ==="
for PREFIX in hermes_ projects_; do
    # shellcheck disable=SC2012
    OLD=$(ls -1t "$BACKUP_DIR/${PREFIX}"*.tar.gz 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)))
    if [[ -n "$OLD" ]]; then
        echo "$OLD" | while read -r F; do
            echo "  Hapus: $F"
            rm -f "$F"
        done
    else
        echo "  Gak ada backup lama yang perlu dihapus."
    fi
done

# ── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════ RINGKASAN BACKUP ═══════════════════════════"
echo "  Tanggal:     $(date)"
echo "  Lokasi:      $BACKUP_DIR"
echo ""
echo "  Dibikin:"
echo "    ● $(ls -lh "$HERMES_ARCHIVE" | awk '{print $5, $NF}')"
echo "    ● $(ls -lh "$PROJECTS_ARCHIVE" | awk '{print $5, $NF}')"
echo ""
echo "  Simpan:      $MAX_BACKUPS backup terakhir per kategori"
echo "  Jumlah:"
echo "    hermes_   →  $(find "$BACKUP_DIR" -maxdepth 1 -name 'hermes_*.tar.gz' | wc -l) backup"
echo "    projects_ →  $(find "$BACKUP_DIR" -maxdepth 1 -name 'projects_*.tar.gz' | wc -l) backup"
echo "═══════════════════════════════════════════════════════════════════════"
