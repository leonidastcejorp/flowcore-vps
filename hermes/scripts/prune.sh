#!/bin/bash
# Prune Hermes sessions older than 30 days
echo "🧹 Pruning sessions older than 30 days..."
hermes sessions prune --older-than 30 2>&1 || echo "prune skipped or not available"
echo "✅ Done at $(date)"
