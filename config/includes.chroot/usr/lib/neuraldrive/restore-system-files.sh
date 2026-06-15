#!/bin/bash
# Restore admin-customized /etc files from the persistence partition.
#
# A handful of system files modified by the first-boot wizard live OUTSIDE
# our `union` persistence entries (which only cover /var/lib/neuraldrive,
# /etc/neuraldrive, /var/log/neuraldrive, /home). Notably:
#
#   * /etc/shadow                          — admin password hash (chpasswd)
#   * /etc/sudoers.d/neuraldrive-admin     — NOPASSWD strip
#
# Without this restore step those changes would be silently undone on every
# reboot: the read-only squashfs lowerdir is replayed and the tmpfs ephemeral
# overlay starts empty, so /etc/shadow reverts to the baked-in default
# (and admins can no longer log in with their chosen password).
#
# The wizard stashes the relevant pieces into /var/lib/neuraldrive/system/,
# which IS in a `union` persistence entry, so the stash survives reboots.
# This script runs as a oneshot before sshd / getty / TUI autologin start.
#
# The restore is per-account / per-file, not whole-file. That way a future
# ISO upgrade that adds new system users to /etc/shadow won't have those
# new entries clobbered by an old saved copy.
set -u

STATE_DIR=/var/lib/neuraldrive/system

if [ ! -d "$STATE_DIR" ]; then
    exit 0
fi

# --- /etc/shadow: replace just the neuraldrive-admin line ---
SHADOW_SRC="$STATE_DIR/neuraldrive-admin.shadow"
if [ -s "$SHADOW_SRC" ]; then
    NEW_LINE=$(head -n1 "$SHADOW_SRC")
    case "$NEW_LINE" in
        neuraldrive-admin:*)
            TMP=$(mktemp /etc/shadow.restore.XXXXXX)
            chmod 640 "$TMP"
            chown root:shadow "$TMP" 2>/dev/null || chown root:root "$TMP"
            if grep -q '^neuraldrive-admin:' /etc/shadow; then
                awk -v new="$NEW_LINE" '
                    /^neuraldrive-admin:/ { print new; next }
                    { print }
                ' /etc/shadow > "$TMP"
            else
                cat /etc/shadow > "$TMP"
                echo "$NEW_LINE" >> "$TMP"
            fi
            mv "$TMP" /etc/shadow
            ;;
        *)
            echo "neuraldrive-restore-system: refusing to apply malformed shadow line" >&2
            ;;
    esac
fi

# --- /etc/sudoers.d/neuraldrive-admin: whole-file replace ---
# This file is owned entirely by us, no upgrade conflict possible.
SUDOERS_SRC="$STATE_DIR/sudoers.d-neuraldrive-admin"
if [ -s "$SUDOERS_SRC" ]; then
    install -m 0440 -o root -g root "$SUDOERS_SRC" /etc/sudoers.d/neuraldrive-admin
fi

exit 0
