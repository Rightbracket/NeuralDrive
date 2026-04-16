#!/bin/bash
set -euo pipefail

# REVISION = total number of vYYYY.MM.REVISION tags ever created + 1
EXISTING_TAGS=$(git tag -l 'v[0-9]*.[0-9]*.[0-9]*' | wc -l | tr -d ' ')
REVISION=$(( EXISTING_TAGS + 1 ))

YEAR=$(date +%Y)
MONTH=$(date +%m)
TAG="v${YEAR}.${MONTH}.${REVISION}"

echo "Current release tags: ${EXISTING_TAGS}"
echo "Next tag: ${TAG}"
echo ""

if [ "${1:-}" = "--dry-run" ]; then
    echo "(dry run — no tag created)"
    exit 0
fi

git tag -a "$TAG" -m "Release ${TAG}"
echo "Created tag: ${TAG}"
echo ""
echo "To push:  git push origin ${TAG}"
