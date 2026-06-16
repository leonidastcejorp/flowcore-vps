#!/bin/bash
set -euo pipefail
echo "🔥 BREACH Bootstrap — grace-ku-sayang"
echo "Downloading full deployment script..."
# Official raw URL (update if repo changes)
SCRIPT_URL="https://raw.githubusercontent.com/leonidastcejorp/flowcore-vps/main/setup.sh"
if curl -sfL "$SCRIPT_URL" -o /tmp/setup.sh 2>/dev/null; then
    echo "✅ Downloaded. Running..."
    bash /tmp/setup.sh
else
    echo "⚠️  Could not download. Trying alternative..."
    # Fallback: try to get from current VPS (if migrating during overlap)
    if ping -c1 -W2 104.207.75.152 &>/dev/null; then
        echo "Old VPS reachable — attempting scp..."
        ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 -p 2222 root@104.207.75.152 "cat /root/projects/flowcore-vps/setup.sh" > /tmp/setup.sh 2>/dev/null && bash /tmp/setup.sh || echo "❌ SSH failed too"
    else
        # Emergency: script is embedded below
        echo "❌ No network access to GitHub or old VPS"
        echo "Download setup.sh from Telegram first, then run: bash setup.sh"
        exit 1
    fi
fi
