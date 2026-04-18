FROM debian:bookworm

RUN apt-get update && apt-get install -y \
    live-build \
    debootstrap \
    squashfs-tools \
    xorriso \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    python3-yaml \
    wget \
    curl \
    git \
    sudo \
    && curl -L https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -o /usr/bin/yq \
    && chmod +x /usr/bin/yq \
    && rm -rf /var/lib/apt/lists/* \
    && cp /usr/lib/grub/i386-pc/boot_hybrid.img /usr/local/share/grub-boot-hybrid.img

COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

WORKDIR /build
