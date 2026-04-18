#!/bin/bash
# Docker build entrypoint for NeuralDrive.
#
# Copies the source tree from the read-only bind mount (/src) into the
# container's own writable filesystem (/build) where live-build can
# freely mknod, mount, and chroot.  The final ISO is written directly
# to the bind-mounted /output directory.
#
# Environment variables:
#   NEURALDRIVE_DEBUG=1   Enable set -x and drop to shell on failure
#   NEURALDRIVE_SHELL=1   Set up workspace then drop to interactive shell
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

if [[ "${NEURALDRIVE_DEBUG:-}" == "1" ]]; then
    set -x
fi

# Patch live-build to add hybrid MBR support for grub-pc bootloader.
# live-build only passes -isohybrid-mbr to xorriso for syslinux; without this
# patch, ISOs built with grub-pc lack a partition table and won't boot from USB.
if ! grep -q 'grub2-mbr' /usr/lib/live/build/binary_iso 2>/dev/null; then
    PATCH_LINE=$(grep -n 'isohybrid-mbr.*/usr/lib/ISOLINUX/isohdpfx.bin' /usr/lib/live/build/binary_iso 2>/dev/null | head -1 | cut -d: -f1) || true
    if [ -n "${PATCH_LINE:-}" ]; then
        # Write patch to temp file — heredoc + sed "r /dev/stdin" conflict
        cat > /tmp/lb-grub-hybrid.patch <<'LIVEBUILD_PATCH'

if [ "${LB_IMAGE_TYPE}" = "iso-hybrid" ] && [ "${LB_BOOTLOADER_BIOS}" = "grub-pc" ]
then
	XORRISO_OPTIONS="${XORRISO_OPTIONS} --grub2-mbr /usr/local/share/grub-boot-hybrid.img --grub2-boot-info -partition_offset 16"
fi
LIVEBUILD_PATCH
        sed -i "$((PATCH_LINE + 1))r /tmp/lb-grub-hybrid.patch" /usr/lib/live/build/binary_iso
        rm -f /tmp/lb-grub-hybrid.patch
        echo "Patched live-build for grub-pc hybrid MBR"
    fi
fi

# Patch live-build to add part_msdos and search modules to grub-mkimage.
# The default binary_grub-pc only embeds "biosdisk iso9660" in grub_eltorito.
# Without part_msdos, GRUB can't parse the MBR partition table on USB hybrid boot,
# so it never finds the ISO9660 filesystem and hangs at "GRUB loading."
if ! grep -q 'part_msdos' /usr/lib/live/build/binary_grub-pc 2>/dev/null; then
    if grep -q 'biosdisk iso9660' /usr/lib/live/build/binary_grub-pc 2>/dev/null; then
        sed -i 's/biosdisk iso9660/biosdisk iso9660 part_msdos search/' /usr/lib/live/build/binary_grub-pc
        echo "Patched live-build binary_grub-pc: added part_msdos and search modules"
    fi
fi

echo "Preparing build workspace..."
cp -a /src/. /build/

# Place boot_hybrid.img where xorriso can find it inside the chroot
# (binary_iso runs xorriso via chroot, not on the host filesystem)
mkdir -p /build/config/includes.chroot/usr/local/share
cp /usr/local/share/grub-boot-hybrid.img /build/config/includes.chroot/usr/local/share/grub-boot-hybrid.img

# Point the output directory at the bind mount so the ISO lands on the
# host filesystem without an extra copy step.
rm -rf /build/output
ln -s /output /build/output
mkdir -p /output

cd /build

if [[ "${NEURALDRIVE_SHELL:-}" == "1" ]]; then
    echo ""
    echo "Workspace ready at /build"
    echo "Output will go to /output"
    echo ""
    echo "Useful commands:"
    echo "  ./build.sh                    # full build"
    echo "  lb config ...                 # configure live-build"
    echo "  lb build                      # build the image"
    echo "  ls chroot/                    # inspect debootstrap output"
    echo ""
    exec bash
fi

if [[ "${NEURALDRIVE_DEBUG:-}" == "1" ]]; then
    ./build.sh "$@" || {
        rc=$?
        echo ""
        echo "Build failed (exit $rc). Dropping to debug shell."
        echo ""
        echo "Useful paths:"
        echo "  /build/                       # workspace root"
        echo "  /build/chroot/                # debootstrap chroot"
        echo "  /build/.build/                # live-build state"
        echo "  /output/                      # output bind mount"
        exec bash
    }
else
    exec ./build.sh "$@"
fi
