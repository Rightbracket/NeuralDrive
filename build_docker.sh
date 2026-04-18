#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

FORCE_BUILD=false
KEEP=false
SHELL_MODE=false
DEBUG=false
BUILD_ARGS=()

usage() {
    cat <<'EOF'
Usage: build_docker.sh [options] [-- build.sh args...]

Build NeuralDrive ISO inside Docker.

Options:
  -f, --force-build   Rebuild Docker image from scratch (no layer cache)
  -k, --keep          Keep container after build finishes
  -s, --shell         Set up workspace then drop into interactive shell
  -d, --debug         Verbose output + interactive shell on failure
  -h, --help          Show this message

Debug workflow:
  ./build_docker.sh -s              # Shell into container, run steps manually:
                                    #   lb config ...
                                    #   lb build
                                    #   ls chroot/
  ./build_docker.sh -d              # Full build; drops to shell on failure
  ./build_docker.sh -d -k           # Same, but keep container after exit too

Examples:
  ./build_docker.sh                              # Standard build
  ./build_docker.sh -f                           # Force image rebuild
  ./build_docker.sh -- neuraldrive-build.yaml    # Custom config
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -f|--force-build) FORCE_BUILD=true; shift ;;
        -k|--keep)        KEEP=true; shift ;;
        -s|--shell)       SHELL_MODE=true; shift ;;
        -d|--debug)       DEBUG=true; shift ;;
        -h|--help)        usage; exit 0 ;;
        --)               shift; BUILD_ARGS=("$@"); break ;;
        -*)               echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
        *)                BUILD_ARGS+=("$1"); shift ;;
    esac
done

if $FORCE_BUILD; then
    docker compose build --no-cache builder
else
    docker compose build builder
fi

mkdir -p output

CMD=(docker compose run)

if ! $KEEP; then
    CMD+=(--rm)
fi

if $SHELL_MODE; then
    CMD+=(-e NEURALDRIVE_SHELL=1)
fi

if $DEBUG; then
    CMD+=(-e NEURALDRIVE_DEBUG=1)
fi

CMD+=(builder)

if [[ ${#BUILD_ARGS[@]} -gt 0 ]]; then
    CMD+=("${BUILD_ARGS[@]}")
fi

exec "${CMD[@]}"
