#!/bin/bash
# /usr/lib/neuraldrive/dev-reset.sh
# Development reset script — restores a post-wizard system to a
# development-friendly state.  Included in builds for convenience.
#
# Usage:  sudo /usr/lib/neuraldrive/dev-reset.sh

set -e

echo "=== NeuralDrive Development Reset ==="
echo ""

# 1. Reset admin password to the build default
echo "neuraldrive-admin:neuraldrive" | chpasswd
echo "[ok] Admin password reset to 'neuraldrive'"

# 2. Restore blanket NOPASSWD for development
echo "neuraldrive-admin ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/neuraldrive-admin
chmod 440 /etc/sudoers.d/neuraldrive-admin
echo "[ok] Blanket NOPASSWD sudo restored"

# 3. Remove wizard sentinel so it runs again on next TUI start
rm -f /etc/neuraldrive/first-boot-complete
echo "[ok] Wizard sentinel removed"

# 4. Clear config files so wizard starts fresh
rm -f /var/lib/neuraldrive/config/config.yaml
rm -f /etc/neuraldrive/config.yaml
echo "[ok] Config files cleared"

# 5. Clear generated credentials
rm -f /etc/neuraldrive/api.key
rm -f /etc/neuraldrive/credentials.conf
echo "[ok] API key and credentials cleared"

echo ""
echo "Development reset complete."
echo "Restart the TUI to re-run the first-boot wizard."
