# NeuralDrive Plan Review Notes

This document captures findings from three review passes of the NeuralDrive implementation plan (files 00-10). Issues are classified by severity and perspective.

---

## Review 1: Implementation Feasibility

### BLOCKING

1. **SquashFS size estimate may be too low** (00-overview.md, Section 2)
   - The overview estimates 4-8 GB for the system partition. With NVIDIA drivers (~3 GB) + CUDA runtime (~4 GB) + ROCm (~6 GB) + Ollama + Open WebUI + Python + all dependencies, the full image with all GPU drivers will likely exceed 12-15 GB.
   - **Resolution**: Build GPU-specific image variants as described in 10-testing-deployment.md Section 8 (neuraldrive-full, neuraldrive-nvidia, neuraldrive-minimal). Update the partition size estimate in 00-overview and 04-storage to reflect realistic sizes per variant.

2. **Ollama .deb package may not exist in official repos** (03-llm-runtime.md, Section 1)
   - Ollama distributes via a shell install script (`curl -fsSL https://ollama.com/install.sh | sh`), not via official Debian repos. The plan references a `.deb` package but this may need to be downloaded during build or packaged manually.
   - **Resolution**: During the `live-build` chroot phase, use a hook script to run the Ollama installer, or download the `.deb` from Ollama's GitHub releases and place it in `config/packages.chroot/`.

### SIGNIFICANT

3. **live-build `--bootloaders grub-efi` flag** (01-base-system.md, Section 2)
   - This flag only configures EFI boot. For hybrid BIOS+EFI boot (required for CD compatibility), use `--bootloaders "grub-efi,grub-pc"` or rely on `isohybrid` post-processing.
   - **Resolution**: Update the `lb config` command to include both bootloader targets.

4. **Open WebUI pip install may be fragile** (07-web-interface.md, Section 1)
   - `pip install open-webui` pulls many dependencies. In a live-build chroot environment, this can fail due to missing system libraries (especially for chromadb, which needs C++ compilation).
   - **Resolution**: Add build-essential and relevant dev packages to the build environment. Consider using `--no-cache-dir` and pinning the Open WebUI version. Test the pip install step early in development.

5. **ROCm packages not in Debian repos** (02-gpu-support.md, Section 2)
   - ROCm packages come from AMD's own repository, not Debian's. The plan correctly shows adding the repo, but this needs to be configured as a live-build archive source, not just a runtime apt source.
   - **Resolution**: Add the ROCm repo configuration to `config/archives/rocm.list.chroot` and `config/archives/rocm.key.chroot`.

6. **GPU detection script runs before modules are available** (02-gpu-support.md, Section 4)
   - The script calls `modprobe nvidia` but in a live system, if DKMS wasn't run, the modules may not exist for the running kernel.
   - **Resolution**: Use pre-compiled kernel modules matching the exact kernel shipped. Verify module existence before `modprobe`. Add error handling: `modprobe nvidia 2>/dev/null || echo "NVIDIA_MODULE_MISSING=true" >> "$GPU_CONF"`.

7. **Missing neuraldrive-ollama user in systemd unit** (03-llm-runtime.md, Section 1)
   - The service file uses `User=neuraldrive` but the user created in 01-base-system.md hooks is `neuraldrive-ollama`. These must match.
   - **Resolution**: Update 03-llm-runtime.md to use `User=neuraldrive-ollama` and `Group=neuraldrive-ollama`.

### MINOR

8. **Build time estimate** (01-base-system.md, Section 6): 15-30 minutes is optimistic if including CUDA/ROCm downloads. 30-90 minutes is more realistic with all GPU stacks.

9. **Docker build needs `--privileged`** (09-image-toolkit.md, Section 4): Correct that privileged is needed for loopback mounts, but this should be documented as a security consideration. Rootless Docker won't work.

10. **Missing `python3` and `python3-venv` in package list** (01-base-system.md, Section 2): The TUI and management API require Python but it's not in the base package list. Add `python3`, `python3-venv`, `python3-pip` to `neuraldrive.list.chroot`.

---

## Review 2: Security

### CRITICAL

1. **API key auth not enforced in Caddyfile** (07-web-interface.md, Section 4)
   - The Caddyfile routes `/v1/*` and `/api/*` directly to Ollama without any authentication middleware. The API key check mentioned in 08-api-services.md relies on application-level auth, but Ollama itself does not enforce API keys natively.
   - **Resolution**: Add Caddy-level authentication. Use `forward_auth` or `basicauth` directives in the Caddyfile for API routes. Alternatively, route API traffic through the management FastAPI app which verifies the Bearer token before proxying to Ollama.

2. **neuraldrive-admin has passwordless sudo** (01-base-system.md, hooks)
   - The chroot hook grants `neuraldrive-admin` passwordless sudo. Even though the first-boot wizard sets a password, the sudoers entry persists. If SSH is enabled, this is a privilege escalation vector.
   - **Resolution**: The first-boot wizard should replace the NOPASSWD sudoers entry with a password-required one after the admin password is set. Add to first-boot completion: `echo "neuraldrive-admin ALL=(ALL) ALL" > /etc/sudoers.d/neuraldrive-admin`.

### HIGH

3. **Self-signed cert with `-k` flag in examples** (08-api-services.md, Section 2)
   - The curl examples use `-k` (disable TLS verification), which trains users to ignore certificate errors. This is a security anti-pattern.
   - **Resolution**: Document how to export and install the NeuralDrive CA certificate on client machines. Show examples using `--cacert /path/to/neuraldrive-ca.crt` instead of `-k`.

4. **mDNS port (5353) open to all** (05-security.md, Section 2)
   - UDP 5353 is open without rate limiting. mDNS amplification attacks are possible.
   - **Resolution**: Add `limit rate 10/second` to the mDNS rule, and consider restricting to link-local source addresses.

### MEDIUM

5. **Credential file permissions** (05-security.md, Section 5): `/etc/neuraldrive/credentials.conf` is chmod 600 but owned by root. The TUI (running as neuraldrive-admin) needs to read it for display. Consider `root:neuraldrive-admin` with 640.

6. **No CORS configuration** (07-web-interface.md): The Caddy config doesn't include CORS headers. Browser-based API clients from other origins would be blocked (or worse, if CORS is too permissive, exploitable).

7. **SystemCallFilter may break GPU drivers** (05-security.md, Section 3): The `@system-service` syscall filter may be too restrictive for NVIDIA's proprietary driver stack which uses unusual ioctls. This needs testing and may require `SystemCallFilter=@system-service @raw-io` for the Ollama service.

### LOW

8. **No intrusion detection**: Consider documenting AIDE or rkhunter as optional add-ons for persistent installations.

9. **Log injection**: The audit log format should sanitize user-supplied data (model names from API requests) before writing to structured JSON logs.

---

## Review 3: User Experience

### BLOCKING UX

1. **No IP address display during boot** (01-base-system.md, 06-local-interface.md)
   - Non-technical users need to know the IP address to access the web dashboard from another device. The plan mentions the TUI shows the IP, but users on a different machine can't see the TUI.
   - **Resolution**: Display the IP address and dashboard URL prominently on the console during boot (before TUI launches). Add a boot message: "NeuralDrive ready! Dashboard: https://192.168.x.x/ or https://neuraldrive.local/". Include this in the MOTD and as a post-boot systemd service that writes to all TTYs.

2. **mDNS unreliable on many networks** (08-api-services.md, Section 5)
   - Corporate networks, some home routers, and Windows machines without Bonjour often can't resolve `.local` addresses. Users may not be able to reach `neuraldrive.local`.
   - **Resolution**: Always display the IP address alongside the mDNS name. Document fallback: "If neuraldrive.local doesn't work, use the IP address shown on the console." Consider adding a simple DHCP hostname registration.

### CONFUSING

3. **First-boot wizard ordering** (06-local-interface.md, Section 6)
   - The wizard asks about LUKS encryption (step 5) after network configuration (step 3). LUKS formatting will destroy any existing data on the partition. This should be the FIRST critical decision, with a clear warning.
   - **Resolution**: Move encryption decision to step 2 (right after welcome/hardware summary). Add a prominent warning: "WARNING: Enabling encryption will format the data partition. This cannot be undone."

4. **CD boot mode is confusing** (04-storage-persistence.md, Section 6)
   - Users who boot from CD see "Model downloads disabled" but may not understand why. The error message should explain: "You booted from CD (read-only media). To download models, connect a USB drive or reboot from a USB stick."
   - **Resolution**: Add explicit, user-friendly messaging for CD mode in the TUI.

5. **Two ports (443 and 8443) is confusing** (07-web-interface.md)
   - Users may not understand why the dashboard is on 443 but the API is on 8443. This split creates confusion for coding agent configuration.
   - **Resolution**: Document clearly: "Port 443 = Web Dashboard (browser). Port 8443 = API (coding agents)." Consider adding API routes to port 443 as well, under a `/api/` prefix, so a single URL works for everything.

### IMPROVEMENT

6. **Model recommendation engine** (03-llm-runtime.md, Section 3): The model catalog is static YAML. The first-boot wizard and TUI should actively recommend models based on detected hardware: "Your RTX 4090 has 24GB VRAM. Recommended: llama3.1:70b-q4 for best quality, or llama3.1:8b for fast responses."

7. **Upgrade documentation** (10-testing-deployment.md): The plan doesn't describe how users update NeuralDrive. Add a section: "Download new ISO → re-flash USB (NDATA partition preserved if partition layout unchanged) or use neuraldrive-update tool."

8. **Quick-start card**: Include a physical/printable quick-start reference with the ISO download: "1. Flash to USB. 2. Boot. 3. Find IP on screen. 4. Open browser to https://[IP]/"

### POLISH

9. **TUI color theme**: Document the color scheme (suggest dark background with green/amber accents for the "terminal server" aesthetic).

10. **Loading indicators**: The TUI should show a spinner/progress during model pulls and service restarts, not just status text.

---

## Cross-Cutting Issues

### Consistency Fixes Applied
- ✅ SSH disabled by default (was enabled in hook — fixed)
- ✅ Model path consistency (`/var/lib/neuraldrive/models/` — fixed in 09)
- ✅ TUI auto-login on tty1 (was missing — added)
- ✅ zram swap setup (was missing — added)
- ✅ Partition creation commands (were missing — added)

### Remaining Consistency Issues
- ~~**Service user mismatch**: 03-llm-runtime.md uses `User=neuraldrive` but should be `User=neuraldrive-ollama` (per 01, 05)~~ — **FIXED**
- ~~**Python not in package list**: 01-base-system.md package list needs `python3 python3-venv python3-pip`~~ — **FIXED**
- ~~**Caddy install not documented**: 07-web-interface.md references `/usr/local/bin/caddy` but no installation step~~ — **FIXED** (added hook 03-install-extras.chroot)
- ~~**fail2ban not in package list**: Referenced in 05-security.md but not in 01-base-system.md package list~~ — **FIXED**
- ~~**Bootloader flag BIOS+EFI**: `lb config` only had `grub-efi`, needed `grub-efi,grub-pc` for hybrid boot~~ — **FIXED** (both instances)

---

## Oracle Review: User Experience (Additional Findings)

The following issues were identified by an independent UX review that read all 11 plan files. These are additional to the self-review findings above.

### BLOCKING UX (Oracle)

11. **First-boot credential flow is internally inconsistent** (06 §6, 05 §5, 07 §2, 01 §2)
    - The wizard says user sets the admin password; the security plan says random password + API key are generated and displayed on TTY; WebUI expects admin email + password. A user would not reliably know what credentials to use for console, WebUI, or API access.
    - **Resolution**: Unify the story: wizard generates random password + API key, displays them, then lets user change the password. WebUI initial admin is provisioned with a username (not email) matching the console output.

12. **No Wi-Fi onboarding flow** (06 §6, 08 §5, 01 §2)
    - NetworkManager and wireless support exist, but the wizard only mentions DHCP vs static IP. On Wi-Fi-only setups, there's no documented way to pick an SSID/password.
    - **Resolution**: Add a Wi-Fi configuration step to the first-boot wizard (before network step). Use `nmcli` or `nmtui` integration.

13. **No headless/remote first-boot path** (01 §4, 06 §6)
    - The system is positioned as a headless server but requires local keyboard/monitor for first-boot setup. No remote or zero-touch setup path exists.
    - **Resolution**: Either document "local console required for first boot" as an explicit constraint, OR add a web-based first-boot wizard accessible after DHCP assigns an IP (before TLS/auth are configured).

14. **Certificate SAN doesn't include IP address** (05 §4)
    - The self-signed cert only covers `neuraldrive.local` and `neuraldrive`. Users falling back to IP address for discovery get HTTPS errors.
    - **Resolution**: The cert generation script should detect the primary IP at first-boot and include it as a SAN: `-addext "subjectAltName=DNS:neuraldrive.local,DNS:neuraldrive,IP:${IP_ADDR}"`.

15. **Python SDK example won't work with self-signed certs** (08 §2)
    - The curl example uses `-k` but the Python SDK example has no SSL verification workaround. It will fail with certificate errors.
    - **Resolution**: Document how to export the CA cert and pass `verify="/path/to/neuraldrive-ca.crt"` to the OpenAI client, or use `REQUESTS_CA_BUNDLE` env var.

### CONFUSING (Oracle)

16. **Upgrade path completely undefined** (05 §9, 09 §6, 10 §7)
    - The plan says updates come as new images but doesn't explain whether users reflash, preserve NDATA, back up models, or migrate between versions.
    - **Resolution**: Add upgrade documentation: "Download new ISO → re-flash USB → NDATA partition is preserved automatically (same partition layout)." Document backup/migration strategy.

17. **CD mode messaging insufficient** (04 §6)
    - Users who boot from CD see "downloads disabled" but need plain-language explanation of why and what to do about it.

18. **Two-port scheme (443 vs 8443) confusing** (07 §4, 08 §1)
    - Users and coding agents must use different ports. Consider routing API through 443 as well under `/api/` prefix.

### Gaps Addressed by This Review
All findings above should be addressed during implementation. The plan is comprehensive and covers all required aspects of the project. The issues identified are implementation-time details that a developer following the plan should resolve, and they are documented here for reference. Key fixes have been applied directly to the plan files where possible; remaining items are clearly flagged for implementation-time resolution.

---

## Review 4: Implementation Readiness Audit

Full cross-file review of all 16 plan documents against the-ask.md requirements. Every requirement from the-ask.md is covered. However, 25 issues were found that would prevent a developer from building a working system from the plan as-written. Issues are categorized by severity.

### Requirements Coverage (the-ask.md → Plan)

All explicit requirements from the-ask.md have corresponding plan coverage:

| Requirement | Covered By |
| :--- | :--- |
| LiveCD/LiveUSB distro | 00, 01 (live-build, Debian 12) |
| Boot from CD or USB | 01 (GRUB, iso-hybrid), 04 (CD/USB modes) |
| Load LLMs from media | 03 (pre-loaded models), 09 (model pre-loading) |
| Download models on USB | 03 (ollama pull), 04 (persistence) |
| Multiple concurrent models | 03 §4 (Ollama concurrency) |
| GPU acceleration | 02 (NVIDIA, AMD, Intel, auto-detection) |
| Lightweight/optimized | 01 (minimal packages), 04 (zram, noatime) |
| Simple accessible UI | 06 (TUI), 07/07a-d (web) |
| Text interface | 06 (Textual TUI) |
| Web interface | 07, 07a-07d (Open WebUI + System Panel) |
| Security | 05 (nftables, hardening, TLS, auth) |
| Data persistence | 04 (partition, overlayfs) |
| Minimal services, SSH optional | 01 (SSH disabled), 05 (SSH hardening) |
| Custom image toolkit | 09 (neuraldrive-builder) |
| Remote access / coding agents | 08 (OpenAI-compatible API, client guides) |
| Storage management | 04 (partition layout, monitoring) |
| CD non-persistent mode | 04 §6 (tmpfs, external storage) |

### BLOCKING — System Will Not Work

**B1. Persistence will not activate — missing boot parameter** (01 §4, 04 §3)
- None of the GRUB menu entries include the `persistence` keyword. Without this kernel parameter, live-boot completely ignores any persistence partition.
- **Fix**: Add `persistence` to the Normal boot entry's kernel parameters.
- **Status**: ✅ FIXED

**B2. Wrong partition label for persistence** (04 §2, §3)
- The plan uses partition label `NDATA`. live-boot requires the exact label `persistence` (case-sensitive, lowercase). A partition labeled `NDATA` will be silently ignored.
- Additionally, `persistence.conf` must be on the root of the persistence partition filesystem, not at `/etc/persistence.conf` as stated in §3.
- **Fix**: Change partition label to `persistence`, fix persistence.conf location description, or use `persistence-label=NDATA` boot parameter.
- **Status**: ✅ FIXED

**B3. No systemd service unit for Caddy** (01 §hooks, 07 §4)
- The binary is downloaded to `/usr/local/bin/caddy` but no `neuraldrive-caddy.service` unit exists. Caddy will never start.
- **Fix**: Add a systemd service unit for Caddy.
- **Status**: ✅ FIXED

**B4. No build hooks for Python components** (01, 06, 07, 08)
- The following components are described but have no chroot build hook to install them:
  - Open WebUI (pip install in venv)
  - GPU Hot (pip install in venv)
  - TUI dependencies (textual, psutil, httpx, rich)
  - System Management API dependencies (fastapi, uvicorn)
- Without these hooks, the image will boot with none of these services available.
- **Fix**: Add hook `04-install-python-apps.chroot` covering all Python components.
- **Status**: ✅ FIXED

**B5. Missing systemctl enables in chroot hook** (01 §hooks)
- Only 4 services are enabled: `neuraldrive-setup`, `neuraldrive-gpu-detect`, `nftables`, `avahi-daemon`.
- Missing enables: `neuraldrive-ollama`, `neuraldrive-webui`, `neuraldrive-caddy`, `neuraldrive-gpu-monitor`, `neuraldrive-tui`, `neuraldrive-zram`, `neuraldrive-system-api`.
- **Fix**: Add all service enables to the chroot hook.
- **Status**: ✅ FIXED

**B6. Certificate generation not wired to boot sequence** (05 §4)
- `generate-certs.sh` is defined but never called. No systemd unit triggers it. Caddy needs certs to start — without them, HTTPS is broken.
- **Fix**: Add a `neuraldrive-certs.service` that runs before Caddy, generating certs on first boot and persisting them.
- **Status**: ✅ FIXED

**B7. Missing config file generation** (07 §1.2, 03 §1)
- The systemd unit references `EnvironmentFile=/etc/neuraldrive/webui.env` but no hook or script creates this file.
- Similarly, `/etc/neuraldrive/ollama.conf` is referenced but not created during build.
- **Fix**: Add config file templates to the build hooks or first-boot script.
- **Status**: ✅ FIXED

**B8. Ollama installation method contradicts between files** (01 §hooks vs 03 §1)
- 01 hook downloads a standalone binary. 03 says "official .deb package." These are different approaches.
- **Fix**: Standardize on the binary download approach (which is what the hook already does). Fix 03 description.
- **Status**: ✅ FIXED

### SIGNIFICANT — Would Cause Confusion or Incorrect Behavior

**S1. First-boot sentinel file inconsistency** (01 §5 vs 06 §6)
- 01 uses `/etc/neuraldrive/initialized` for the setup service.
- 06 uses `/etc/neuraldrive/first-boot-complete` for the TUI wizard.
- These may be intentionally different (system init vs user wizard), but the relationship is not documented.
- **Fix**: Document that these are two separate concerns: system initialization (runs once silently) and user setup wizard (interactive, runs after system init).
- **Status**: ✅ FIXED

**S2. TUI has two startup mechanisms** (01 §hooks vs 06 §1)
- 01 configures autologin + `.profile` to exec the TUI on tty1.
- 06 defines a `neuraldrive-tui.service` systemd unit.
- Both attempt to run the TUI, which would conflict.
- **Fix**: Use `.profile` method (01) for interactive TUI. Remove the systemd service from 06 — TUI is an interactive terminal app, not a background service.
- **Status**: ✅ FIXED

**S3. System Management API split across two files** (07 §6 vs 08 §4)
- 07 has a skeleton with `GET /status` and `POST /services/{name}/restart`.
- 08 has a different skeleton with `GET /system/status`, `GET /system/logs`, `POST /system/ssh/{action}`.
- Different path prefixes and different endpoints.
- The web design (07c) references 10 endpoints, only 3 exist in either skeleton.
- **Fix**: Consolidate into 08 as the canonical API definition. Add all missing endpoints. Update 07 to reference 08.
- **Status**: ✅ FIXED

**S4. Persistence partition is a post-dd step, not first-boot** (04 §2, §8)
- The plan says first-boot creates the NDATA partition. But live-build creates a fixed-size ISO. After `dd`ing to USB, there IS free space, but partition creation requires running a partitioning tool AFTER writing the ISO — either manually or via a helper script bundled separately.
- live-boot's official documentation confirms this is a post-dd step.
- Also: re-flashing the ISO destroys ALL partitions including persistence.
- **Fix**: Document the two-step USB setup process and update the upgrade path.
- **Status**: ✅ FIXED

**S5. API routes in Caddyfile have no authentication** (07 §4, 11 Security §1)
- `/v1/*` and `/api/*` route directly to Ollama without auth. Ollama has no native auth. Anyone on the network can use the API.
- **Fix**: Add Caddy-level bearer token authentication for `/v1/*` and `/api/*` routes. Use environment variable `{env.NEURALDRIVE_API_KEY}` loaded via systemd `EnvironmentFile`. Unauthenticated requests receive 401. System Management API at `/system/*` uses its own FastAPI-level auth.
- **Status**: ✅ FIXED

**S6. SUDOERS NOPASSWD not removed after first-boot** (01 §hooks, 11 Security §2)
- Flagged in prior review but fix not applied to any plan file.
- **Fix**: Add sudoers update to first-boot wizard completion step.
- **Status**: ✅ FIXED

**S7. ROCm archive files missing from build config** (02 §2, 11 §5)
- ROCm repo setup is shown as runtime commands, not as live-build archive sources.
- **Fix**: Add `config/archives/rocm.list.chroot` and `config/archives/rocm.key.chroot`.
- **Status**: ✅ FIXED

**S8. Model pre-loading during build is undefined** (03 §3, 09 §5)
- 03 says "run `ollama pull` during chroot" but Ollama needs to be running as a server.
- 09 describes a `models.squashfs` overlay approach.
- Neither provides a working build script.
- **Fix**: Document the two-phase approach: start Ollama temporarily during build, pull models, stop it. Provide the script.
- **Status**: ✅ FIXED

### MINOR — Documentation Gaps

**M1.** Overview table (00 §4) doesn't list 07a-07d companion design documents.
**M2.** Wi-Fi onboarding not in wizard steps (flagged in prior review, not addressed).
**M3.** Headless first-boot not documented as an explicit constraint.
**M4.** mDNS rate limiting not applied to nftables rules.
**M5.** GPU Hot package availability on PyPI unverified — may need a custom wrapper.
**M6.** Upgrade path still not documented beyond "re-flash ISO."
**M7.** Missing `neuraldrive-system-api` user in service users list (05 §3).
