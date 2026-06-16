#!/bin/bash
# Hapus session Hermes yang lebih lama dari 30 hari
echo "🧹 Hapus session Hermes yang lebih dari 30 hari..."
hermes sessions prune --older-than 30 --yes 2>&1 || hermes sessions prune --older-than 30 -y 2>&1 || echo "❌ Gagal prune (mungkin fitur gak tersedia)"
echo "✅ Selesai $(date)"
