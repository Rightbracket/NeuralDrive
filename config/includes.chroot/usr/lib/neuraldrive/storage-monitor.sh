#!/bin/bash
THRESHOLD_WARN=80
THRESHOLD_CRITICAL=90
THRESHOLD_BLOCK=95

while true; do
    if [ -d /var/lib/neuraldrive/models ]; then
        USAGE=$(df /var/lib/neuraldrive/models --output=pcent 2>/dev/null | tail -1 | tr -d ' %')
        if [ -n "$USAGE" ]; then
            if [ "$USAGE" -ge "$THRESHOLD_BLOCK" ]; then
                echo "$(date -Iseconds) CRITICAL: Storage at ${USAGE}%% — blocking further downloads" >> /var/log/neuraldrive/storage.log
            elif [ "$USAGE" -ge "$THRESHOLD_CRITICAL" ]; then
                echo "$(date -Iseconds) CRITICAL: Storage at ${USAGE}%%" >> /var/log/neuraldrive/storage.log
            elif [ "$USAGE" -ge "$THRESHOLD_WARN" ]; then
                echo "$(date -Iseconds) WARNING: Storage at ${USAGE}%%" >> /var/log/neuraldrive/storage.log
            fi
        fi
    fi
    sleep 60
done
