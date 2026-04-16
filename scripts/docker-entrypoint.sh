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

if [[ "${NEURALDRIVE_DEBUG:-}" == "1" ]]; then
    set -x
fi

echo "Preparing build workspace..."
cp -a /src/. /build/

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
