#!/bin/bash
if [ ! -f /etc/neuraldrive/initialized ]; then
    ssh-keygen -A
    hostnamectl set-hostname neuraldrive

    # Update /etc/hosts so hostname resolves (prevents "unable to resolve host" errors)
    if ! grep -q "neuraldrive" /etc/hosts; then
        sed -i 's/127\.0\.0\.1.*/127.0.0.1\tlocalhost neuraldrive/' /etc/hosts
    fi

    CORES=$(nproc --all 2>/dev/null || echo 4)
    if [ -f /etc/neuraldrive/ollama.conf ]; then
        if ! grep -q "OLLAMA_NUM_THREADS" /etc/neuraldrive/ollama.conf; then
            echo "OLLAMA_NUM_THREADS=${CORES}" >> /etc/neuraldrive/ollama.conf
        fi
    fi

    touch /etc/neuraldrive/initialized
fi
