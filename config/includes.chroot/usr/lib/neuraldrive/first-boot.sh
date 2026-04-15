#!/bin/bash
if [ ! -f /etc/neuraldrive/initialized ]; then
    ssh-keygen -A
    hostnamectl set-hostname neuraldrive

    CORES=$(nproc --all 2>/dev/null || echo 4)
    if [ -f /etc/neuraldrive/ollama.conf ]; then
        if ! grep -q "OLLAMA_NUM_THREADS" /etc/neuraldrive/ollama.conf; then
            echo "OLLAMA_NUM_THREADS=${CORES}" >> /etc/neuraldrive/ollama.conf
        fi
    fi

    touch /etc/neuraldrive/initialized
fi
