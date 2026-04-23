# NeuralDrive Known Bugs

## Fixed (Build 14)

### ~~1. No persistence partition creation on first boot~~
**Status**: Deferred — requires runtime logic in wizard Step 4. Partition creation at runtime is complex (needs to detect boot device, resize, mkfs while live). Documented for future implementation.

### ~~2. TUI mouse capture over SSH~~
**Fixed**: Disabled mouse capture in `main.py` with `app.run(mouse=False)`. Keyboard navigation (Tab/Shift+Tab/Enter/Escape) works natively.

### ~~3. TUI black screen after wizard completion~~
**Fixed**: `main.py on_mount()` now always pushes `DashboardScreen()` first, then overlays `FirstBootWizard()` on top. When wizard finishes and pops, dashboard is underneath.

### ~~4. WebUI 502 — port mismatch~~
**Fixed**: Caddyfile updated from `reverse_proxy localhost:3000` to `reverse_proxy localhost:8080`. Open WebUI v0.9.1 listens on 8080 by default.

### ~~5. Console terminal geometry wrong~~
**Fixed**: Removed `nvidia-drm.modeset=1` from Normal boot kernel cmdline in `grub.cfg`. Without KMS modeset, VGA text console stays at native 80×25 on the physical display. NVIDIA driver still loads for CUDA compute (ollama). The display path is no longer hijacked by nvidia-drm.

### ~~6. fail2ban crash~~
**Fixed**: Changed jail config from `logpath = /var/log/auth.log` to `backend = systemd`. Reads SSH auth events from journald instead of a log file that may not exist on a live system.

### ~~7. Caddy home dir permission errors~~
**Fixed**: Added `XDG_DATA_HOME=/var/lib/neuraldrive/caddy` and `XDG_CONFIG_HOME=/var/lib/neuraldrive/caddy/config` environment variables to `neuraldrive-caddy.service`. Directory created and owned by neuraldrive-caddy user in `01-setup-system.chroot`. Added `/var/lib/neuraldrive/caddy` to `ReadWritePaths`.

## Remaining

### 8. GPU conf stale after boot
**Symptom**: `/run/neuraldrive/gpu.conf` says `NVIDIA_MODULE_MISSING=true` but nvidia-smi works fine.
**Root cause**: `gpu-detect.sh` runs before nvidia modules fully load. Cosmetic only.
**Fix**: Add retry/delay to gpu-detect.sh, or re-run after modules load.

### 9. NVIDIA driver upgrade to 545+
**Symptom**: No framebuffer console on local display with nvidia GPU. Console stuck at VGA 80×25.
**Root cause**: Driver 535.x lacks `nvidia-drm.fbdev=1` parameter (added in 545+). With `fbdev=1`, the driver creates a DRM framebuffer that `fbcon` uses for a full-resolution console.
**Fix**: Upgrade from `nvidia-kernel-dkms 535.x` to 545+ in `config/package-lists/gpu-nvidia.list.chroot`. Add `nvidia-drm.fbdev=1` to kernel cmdline in `grub.cfg`. Also install `console-setup` package with appropriate font for high-DPI displays.
**Note**: With the removal of `nvidia-drm.modeset=1` in build 14, VGA text console works correctly at 80×25. This upgrade would provide a full-resolution console but is not required for functionality.

### 10. Persistence partition creation
**Symptom**: 500GB USB shows only ~8GB overlay. Remaining space unpartitioned.
**Root cause**: `prepare-usb.sh` exists but is only called by `neuraldrive-flash.sh` (Linux-only). Mac/Windows flash methods (dd, Etcher) skip it. TUI wizard Step 4 only displays storage info — doesn't create partitions.
**Fix**: Wizard Step 4 should detect missing persistence partition and offer to create it using boot device from `detect-media.sh` + `prepare-usb.sh` logic.
