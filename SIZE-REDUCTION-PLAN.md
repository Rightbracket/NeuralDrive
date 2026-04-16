# NeuralDrive ISO Size Reduction Plan

**Goal**: Reduce ISO from ~32GB to ~8-12GB  
**Status**: ✅ COMPLETE — Final ISO: 3.9GB  
**Date**: 2026-04-16

---

## Strategy 1: Minimal open-webui Install (~2.5-3GB saved)

**Status**: READY TO IMPLEMENT

**Problem**: `pip install open-webui` transitively pulls ~3.5GB+ of packages including PyTorch (~530MB), nvidia-cudnn (~366MB), nvidia-cublas (~423MB), triton (~188MB), transformers, sentence-transformers, faster-whisper, etc.

**Solution**: Install open-webui with `--no-deps`, then install only the minimal requirements from upstream's `requirements-min.txt`.

**Key Finding**: open-webui has `backend/requirements-min.txt` (36 packages) that excludes all ML/model libraries. The ~50 omitted packages are exactly where the ~3GB torch/CUDA dependency chain lives. Chat proxy to Ollama works fine without torch — torch is only needed for local RAG embeddings (sentence-transformers) and audio transcription (faster-whisper), both lazy-loaded.

**Implementation**:
1. `pip install --no-deps open-webui` to get the wheel without dependencies
2. Create a local requirements-min.txt (pinned from upstream) and `pip install -r requirements-min.txt`
3. Set `USE_SLIM=true` environment variable (disables torch-dependent code paths)

**Minimal deps (36 packages)**:
- Web framework: fastapi, uvicorn, pydantic, python-multipart, starlette-compress
- Auth: python-jose, cryptography, bcrypt, argon2-cffi, PyJWT, authlib
- HTTP: requests, aiohttp, async-timeout, httpx, aiocache, aiofiles
- DB: sqlalchemy, alembic, peewee, peewee-migrate, redis, chromadb
- LLM: openai, langchain, langchain-community, langchain-classic, langchain-text-splitters, mcp
- Utils: APScheduler, RestrictedPython, loguru, asgiref, pycrdt, fake-useragent, black, pydub, chardet, beautifulsoup4, Brotli, python-socketio, itsdangerous, starsessions

**Risk**: ChromaDB (in minimal deps) may transitively pull some heavy packages. Monitor pip output. If it pulls torch, pin chromadb deps or use `--no-deps` for chromadb too.

---

## Strategy 2: Switch to NVIDIA Headless Packages (~1.5-2.5GB saved)

**Status**: READY TO IMPLEMENT (with caveats)

**Problem**: `nvidia-driver` pulls in X11, GLX, and GUI libraries (~2-3GB): `nvidia-driver-libs` (OpenGL/GLX/EGL/GLES), `xserver-xorg-video-nvidia` (Xorg driver), `nvidia-vdpau-driver`.

**Research Result**: **No `nvidia-headless` metapackage exists in Debian bookworm** (Ubuntu-only). Must manually select individual packages.

**Solution**: Replace `nvidia-driver` with minimal headless packages:
```
nvidia-driver-bin          # Driver support binaries
nvidia-smi                 # Already present — monitoring
nvidia-persistenced        # Already present — persistence daemon
firmware-nvidia-gsp        # GSP firmware for Turing+ GPUs
libcuda1                   # CUDA driver library (needed by Ollama)
libnvidia-ml1              # NVML library (needed by nvidia-smi)
```

**CRITICAL CAVEAT**: `nvidia-kernel-dkms` provides the kernel module. Without it, CUDA doesn't work. However:
- It was already removed in iteration 1 (chroot can't build it without matching kernel headers)
- `nvidia-driver` metapackage would pull it back in
- For live-build, DKMS installs source but can't compile in chroot — module builds at first boot IF linux-headers are present
- Decision: Include `nvidia-kernel-dkms` + `dkms` + `linux-headers-amd64` in the headless list. The DKMS source install is small; the X11 deps are what's heavy.

**Final package list**:
```
dkms
nvidia-kernel-dkms
nvidia-driver-bin
nvidia-smi
nvidia-persistenced
firmware-nvidia-gsp
libcuda1
libnvidia-ml1
```

**Risk**: Medium. If nvidia-driver-bin has hard deps on X11 libs, may need to fall back to keeping nvidia-driver. Test during build.

---

## Strategy 3: Add Build-Time Cleanup Hook (~0.5-1GB saved)

**Status**: READY TO IMPLEMENT

**Problem**: build-essential, python3-dev, and other build-time packages remain in the final image. No cleanup hook exists.

**Solution**: Create `config/hooks/live/99-cleanup.chroot` to remove build-time packages and clean caches.

**Implementation**:
```bash
#!/bin/bash
set -e

# Remove build-time packages no longer needed
apt-get purge -y --auto-remove \
    build-essential \
    python3-dev \
    gcc \
    g++ \
    cpp \
    make \
    dpkg-dev \
    libc6-dev \
    linux-libc-dev \
    libstdc++-12-dev \
    zstd

# Clean apt caches
apt-get clean
rm -rf /var/lib/apt/lists/*
rm -rf /var/cache/apt/archives/*

# Clean pip caches
rm -rf /root/.cache/pip
rm -rf /tmp/pip-*

# Clean other caches
rm -rf /tmp/*
rm -rf /var/tmp/*
```

**Risk**: Low. These packages are only needed during hook execution (pip builds native extensions). By hook 99, all pip installs are done.

---

## Strategy 4: Trim Firmware Packages (~minimal savings — DOWNGRADED)

**Status**: DOWNGRADED — savings negligible

**Problem (original)**: `firmware-linux-nonfree` was thought to pull ~0.8-2GB of unnecessary firmware.

**Research Result**: `firmware-linux-nonfree` is a metapackage that only depends on:
- `firmware-amd-graphics` (~80MB) — AMD GPU firmware ← **NEEDED**
- `firmware-misc-nonfree` (~12MB) — contains i915 Intel GPU firmware ← **NEEDED**
- `amd64-microcode` + `intel-microcode` (recommends, skipped by `--apt-recommends false`)

Both `firmware-amd-graphics` and `firmware-misc-nonfree` are **already explicitly listed** in `neuraldrive.list.chroot`. The metapackage is redundant but removing it saves 0 bytes since its deps are already there.

**Revised action**: Simply remove the redundant `firmware-linux-nonfree` line from `neuraldrive.list.chroot`. Add `firmware-nvidia-gsp` (needed for Strategy 2 headless packages). No significant size savings.

**Risk**: None.

---

## Strategy 5: Remove Dead ROCm Repo + SquashFS xz Compression

**Status**: READY TO IMPLEMENT

**Problem**: 
1. ROCm repo (`config/archives/rocm.list.chroot`) still configured despite all ROCm packages being removed — adds apt fetch overhead during build.
2. No SquashFS compression flag set in `lb config` — defaults to gzip. xz gives ~20-30% better compression.

**Solution**:
1. Delete `config/archives/rocm.list.chroot` and `config/archives/rocm.key.chroot` (if exists)
2. Add `--compression xz` to the `lb config` call in `build.sh`

**Implementation**:
- Remove/empty ROCm archive files
- In `build.sh`, add `--compression xz` to the `lb config` command (around line 49-60)

**Risk**: xz compression is slower than gzip but this only affects build time, not runtime. The resulting ISO is smaller.

---

## Progress Tracking

| Strategy | Status | Saved | Notes |
|----------|--------|-------|-------|
| 1. Minimal open-webui | ✅ DONE | ~2.5-3GB | --no-deps + requirements-min.txt in hook 04 |
| 2. NVIDIA headless | ✅ DONE | ~1.5-2.5GB | Manual headless package selection + linux-headers |
| 3. Cleanup hook | ✅ DONE | ~0.5-1GB | 99-cleanup.chroot created |
| 4. Firmware trim | ✅ DONE | ~0 | Removed redundant metapackage line |
| 5. ROCm + xz | ✅ DONE | misc + compression | ROCm files deleted, --compression xz added |

**Total expected savings**: ~4.5-6.5GB from package reduction + ~20-30% better compression on remainder

---

## Build Log

- Iteration 1: Disk space failure → removed nvidia-cuda-toolkit, ROCm packages
- Iteration 2: Ollama 404 → fixed URL to .tar.zst
- Iteration 3: gpu-hot not on PyPI → fixed to git clone
- Iteration 4: gpu-hot fix confirmed in files but build used old code (save.log shows error)
- Iteration 5: All 5 size reduction strategies implemented. GLX alternatives hook failed (5020-update-glx-alternative). Fixed with 5019 pre-hook to remove glx-alternative packages.
- Iteration 6: 5019 purge broke apt deps for hook 03. Fixed by replacing purge with stub alternative registration (mkdir + update-alternatives --install).
- Iteration 7: ✅ BUILD SUCCEEDED. All hooks passed. ISO: 3.9GB (SHA256: f1970d205ebdb4b80e088fe6477f47069f64cbf3ce5f198428fec3f7fb976f99)
