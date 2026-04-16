# Audit Report: plan/11-review-notes.md

Every item in the file has been checked against the actual implementation. Verdicts use:
- **✅ VERIFIED** — fix is present in code/docs
- **⚠️ PARTIAL** — partially addressed, notable gap remains
- **❌ NOT ADDRESSED** — no implementation found
- **N/A** — not applicable to implementation (plan-level concern only)

---

## Review 1: Implementation Feasibility (10 items)

| # | Issue | Severity | Verdict | Evidence |
|---|---|---|---|---|
| 1 | SquashFS size estimate too low | BLOCKING | **N/A** | Planning concern about estimate accuracy. Implementation builds a single image via `build.sh`. GPU-specific variant builds are not implemented, but this is a build-matrix concern, not a code defect. |
| 2 | Ollama .deb may not exist | BLOCKING | **✅ VERIFIED** | `03-install-extras.chroot:7` downloads binary via `curl -fsSL https://ollama.com/download/ollama-linux-amd64`. No .deb used. |
| 3 | Bootloader flag EFI-only | SIGNIFICANT | **✅ VERIFIED** | `build.sh:53`: `--bootloaders "grub-efi,grub-pc"` |
| 4 | pip install fragility | SIGNIFICANT | **⚠️ PARTIAL** | `neuraldrive.list.chroot:46-47` has `build-essential` and `python3-dev` ✅. `04-install-python-apps.chroot` uses `--no-cache-dir` ✅. However, Open WebUI version is **not pinned** (`pip install open-webui` without `==version`). |
| 5 | ROCm not in Debian repos | SIGNIFICANT | **✅ VERIFIED** | `config/archives/rocm.list.chroot` exists as a live-build archive source. |
| 6 | GPU detection modprobe error | SIGNIFICANT | **✅ VERIFIED** | `gpu-detect.sh` has `modprobe nvidia 2>/dev/null \|\| echo "NVIDIA_MODULE_MISSING=true"`. |
| 7 | Service user mismatch | SIGNIFICANT | **✅ VERIFIED** | `neuraldrive-ollama.service:10`: `User=neuraldrive-ollama`. Matches user created at `01-setup-system.chroot:6`. |
| 8 | Build time estimate | MINOR | **✅ VERIFIED** | `build.sh:65`: "This will take 30-90 minutes" — matches realistic estimate. |
| 9 | Docker needs --privileged | MINOR | **✅ VERIFIED** | `docker-compose.yml:7`: `privileged: true`. Documented implicitly in README build instructions. |
| 10 | Python missing from packages | MINOR | **✅ VERIFIED** | `neuraldrive.list.chroot:41-43`: `python3`, `python3-venv`, `python3-pip`. |

**Score: 8/10 VERIFIED, 1 PARTIAL, 1 N/A**

---

## Review 2: Security (9 items)

| # | Issue | Severity | Verdict | Evidence |
|---|---|---|---|---|
| 1 | API key auth not in Caddyfile | CRITICAL | **✅ VERIFIED** | `Caddyfile:17-31`: `@api_authenticated` matcher checks `Authorization "Bearer {env.NEURALDRIVE_API_KEY}"`. Unmatched API routes get 401. |
| 2 | NOPASSWD sudo persists | CRITICAL | **✅ VERIFIED** | `wizard.py:202-207`: `_finalize()` reads sudoers file and does `content.replace("NOPASSWD:", "")`. |
| 3 | -k flag in curl examples | HIGH | **✅ VERIFIED** | `docs/user-guide/src/api/curl-examples.md` uses `--cacert neuraldrive-ca.crt` for all examples. `tls-trust.md` documents full CA install for all platforms. Only `-k` usage is for the initial CA cert download itself (unavoidable bootstrap). |
| 4 | mDNS port open without limit | HIGH | **✅ VERIFIED** | `nftables.conf:20`: `udp dport 5353 limit rate 10/second accept`. |
| 5 | Credential file permissions | MEDIUM | **⚠️ PARTIAL** | `wizard.py:218`: `os.chmod(CREDENTIALS_PATH, 0o600)` — file is 600, owned by the TUI user (neuraldrive-admin). Review suggested `root:neuraldrive-admin 640` for explicit separation. Functionally works but doesn't match the suggested fix exactly. |
| 6 | No CORS configuration | MEDIUM | **❌ NOT ADDRESSED** | Caddyfile has no CORS headers or `header` directives. |
| 7 | SystemCallFilter vs GPU | MEDIUM | **✅ VERIFIED** | `neuraldrive-ollama.service` has **no** `SystemCallFilter` directive at all. Since the filter isn't applied, GPU ioctls can't be broken by it. Issue is moot. |
| 8 | No intrusion detection docs | LOW | **❌ NOT ADDRESSED** | No reference to AIDE, rkhunter, or intrusion detection in docs or configs. |
| 9 | Log injection sanitization | LOW | **❌ NOT ADDRESSED** | `main.py` uses standard FastAPI logging. No structured JSON audit log, no sanitization of user-supplied model names. |

**Score: 6/9 VERIFIED, 1 PARTIAL, 3 NOT ADDRESSED (all medium/low)**

---

## Review 3: User Experience (10 items)

| # | Issue | Severity | Verdict | Evidence |
|---|---|---|---|---|
| 1 | No IP display at boot | BLOCKING | **✅ VERIFIED** | `neuraldrive-show-ip.service` runs `show-ip.sh` which prints IP, dashboard URL, API URL, and mDNS name to console. Created by `02-setup-autologin.chroot:18-30`. |
| 2 | mDNS unreliable on networks | BLOCKING | **✅ VERIFIED** | `show-ip.sh` displays IP address alongside mDNS. TUI dashboard shows IP. Quick-start docs mention both. |
| 3 | Wizard ordering (LUKS after network) | CONFUSING | **⚠️ PARTIAL** | Wizard has no LUKS/encryption step at all (steps: Welcome → Security → WiFi → Network → Storage → Models → Done). The confusing ordering is gone by omission, but encryption setup isn't offered in the wizard. |
| 4 | CD mode messaging | CONFUSING | **❌ NOT ADDRESSED** | `detect-media.sh` writes `NEURALDRIVE_IS_CD` to `/run/neuraldrive/media.conf`, but TUI has zero references to CD mode, IS_CD, or read-only media messaging. |
| 5 | Two ports confusing | CONFUSING | **⚠️ PARTIAL** | `show-ip.sh` shows both ports. Docs explain the split. But API is still exclusively on 8443 — not also routed through 443 under `/api/` as suggested. |
| 6 | Model recommendations by hardware | IMPROVEMENT | **❌ NOT ADDRESSED** | Wizard step 5 says "Models can be pulled after setup" with no hardware-based recommendations. `neuraldrive-models.yaml` has size tiers (small/medium/large with ram/vram requirements) but the wizard doesn't read it. |
| 7 | Upgrade documentation | IMPROVEMENT | **✅ VERIFIED** | `docs/user-guide/src/admin/updating.md` has full upgrade procedure, backup instructions, version checking, and future plans. |
| 8 | Quick-start card | IMPROVEMENT | **⚠️ PARTIAL** | `docs/user-guide/src/getting-started/quick-start.md` exists as a 7-step digital guide. No separate printable/physical card format. |
| 9 | TUI color theme | POLISH | **✅ VERIFIED** | `styles.tcss` implements dark background (#0A0A0A) with amber (#F59E0B) accents — the "terminal server" aesthetic. 206 lines of comprehensive theming. |
| 10 | Loading indicators | POLISH | **⚠️ PARTIAL** | `models.py:64-79` shows real-time percentage progress during model pulls ✅. Service start/stop/restart in `services.py` show ✓/✗ result feedback but no spinner during the operation. |

**Score: 4/10 VERIFIED, 4 PARTIAL, 2 NOT ADDRESSED**

---

## Cross-Cutting Issues

### Consistency Fixes Applied (5 items — all marked ✅ in plan)

| Fix | Verdict | Evidence |
|---|---|---|
| SSH disabled by default | **✅ VERIFIED** | `01-setup-system.chroot:4`: `systemctl disable ssh` |
| Model path consistency | **✅ VERIFIED** | `ollama.conf:2`: `OLLAMA_MODELS=/var/lib/neuraldrive/models/` |
| TUI auto-login on tty1 | **✅ VERIFIED** | `02-setup-autologin.chroot:4-9`: getty autologin override for tty1 |
| zram swap setup | **✅ VERIFIED** | `neuraldrive-zram.service` exists, enabled at `01-setup-system.chroot:32` |
| Partition creation commands | **✅ VERIFIED** | `prepare-usb.sh` has full `parted`/`mkfs.ext4` flow |

### Remaining Consistency Issues (5 items — all marked FIXED in plan)

| Fix | Verdict | Evidence |
|---|---|---|
| Service user mismatch | **✅ VERIFIED** | `neuraldrive-ollama.service:10`: `User=neuraldrive-ollama` |
| Python in package list | **✅ VERIFIED** | `neuraldrive.list.chroot:41-43` |
| Caddy install documented | **✅ VERIFIED** | `03-install-extras.chroot:4-5` downloads Caddy binary |
| fail2ban in package list | **✅ VERIFIED** | `neuraldrive.list.chroot:38`: `fail2ban` |
| Bootloader flag BIOS+EFI | **✅ VERIFIED** | `build.sh:53`: `--bootloaders "grub-efi,grub-pc"` |

**Score: 10/10 VERIFIED**

---

## Oracle Review (8 items)

| # | Issue | Severity | Verdict | Evidence |
|---|---|---|---|---|
| 11 | Credential flow inconsistent | BLOCKING | **✅ VERIFIED** | `wizard.py`: Step 1 sets admin password via `chpasswd`; step 6 generates API key via `secrets.token_urlsafe(32)` and writes to `api.key` + `credentials.conf`. |
| 12 | No WiFi onboarding | BLOCKING | **✅ VERIFIED** | `wizard.py:77-86`: Step 2 "WiFi (Optional)" collects SSID/PSK. `_configure_wifi()` at line 172 calls `nmcli device wifi connect`. |
| 13 | No headless first-boot path | BLOCKING | **⚠️ PARTIAL** | Docs describe NeuralDrive as "headless server" but don't explicitly state "local console required for first boot." No web-based alternative wizard. |
| 14 | Cert SAN missing IP | BLOCKING | **✅ VERIFIED** | `generate-certs.sh:5-8`: Detects IP and appends `IP:${IP_ADDR}` to SAN. |
| 15 | Python SDK certs won't work | BLOCKING | **✅ VERIFIED** | `python-sdk.md:17-29` shows `httpx.Client(verify=CA_CERT_PATH)`. `tls-trust.md:45` documents `REQUESTS_CA_BUNDLE`. |
| 16 | Upgrade path undefined | CONFUSING | **✅ VERIFIED** | `docs/user-guide/src/admin/updating.md` covers full upgrade procedure. |
| 17 | CD mode messaging | CONFUSING | **❌ NOT ADDRESSED** | Same as Review 3 #4. TUI has no CD mode detection or messaging. |
| 18 | Two-port scheme confusing | CONFUSING | **⚠️ PARTIAL** | Same as Review 3 #5. Documented but not consolidated onto single port. |

**Score: 5/8 VERIFIED, 2 PARTIAL, 1 NOT ADDRESSED**

---

## Review 4: Implementation Readiness (23 items)

### BLOCKING (B1–B8) — all marked ✅ FIXED in plan

| # | Issue | Verdict | Evidence |
|---|---|---|---|
| B1 | Missing `persistence` boot param | **✅ VERIFIED** | `grub.cfg:17`: `persistence` in kernel args |
| B2 | Wrong partition label | **✅ VERIFIED** | `prepare-usb.sh:20`: `mkfs.ext4 -L persistence` |
| B3 | No Caddy service unit | **✅ VERIFIED** | `neuraldrive-caddy.service` exists with `ExecStart=/usr/local/bin/caddy run` |
| B4 | No Python build hooks | **✅ VERIFIED** | `04-install-python-apps.chroot` creates 4 venvs (webui, gpu-monitor, tui, api) |
| B5 | Missing service enables | **✅ VERIFIED** | `01-setup-system.chroot:24-36` enables 13 services |
| B6 | Cert generation not wired | **✅ VERIFIED** | `neuraldrive-certs.service` with `Before=neuraldrive-caddy.service` |
| B7 | Missing config files | **✅ VERIFIED** | `ollama.conf` and `webui.env` exist as static includes |
| B8 | Ollama install method conflict | **✅ VERIFIED** | `03-install-extras.chroot:7-8` downloads binary (no .deb) |

### SIGNIFICANT (S1–S8) — all marked ✅ FIXED in plan

| # | Issue | Verdict | Evidence |
|---|---|---|---|
| S1 | Sentinel file inconsistency | **⚠️ PARTIAL** | Two separate files exist (`initialized` in `first-boot.sh:2`, `first-boot-complete` in `wizard.py:12`) — they serve different purposes. But this dual-sentinel design isn't documented in code comments. |
| S2 | TUI two startup mechanisms | **✅ VERIFIED** | Only `.profile` method in `02-setup-autologin.chroot:11-16`. No `neuraldrive-tui.service` exists. |
| S3 | API split across files | **✅ VERIFIED** | Single consolidated `main.py` with 13 endpoints under `/system/*`. |
| S4 | Persistence is post-dd | **✅ VERIFIED** | `prepare-usb.sh` handles post-dd partition creation. Quick-start shows two-step process. `updating.md` warns about partition destruction. |
| S5 | API routes no auth | **✅ VERIFIED** | Same as Sec-Crit-1. Caddyfile has bearer auth. |
| S6 | NOPASSWD not removed | **✅ VERIFIED** | Same as Sec-Crit-2. wizard.py removes NOPASSWD. |
| S7 | ROCm archive missing | **✅ VERIFIED** | `config/archives/rocm.list.chroot` exists. |
| S8 | Model pre-loading undefined | **✅ VERIFIED** | `scripts/seed-models.sh` implements two-phase approach (start ollama, pull, stop, stage). |

### MINOR (M1–M7)

| # | Issue | Verdict | Evidence |
|---|---|---|---|
| M1 | Overview table missing 07a-07d | **N/A** | Plan document concern only. Implementation has full docs coverage. |
| M2 | WiFi not in wizard | **✅ VERIFIED** | `wizard.py:77-86`: Step 2 WiFi. |
| M3 | Headless not documented as constraint | **⚠️ PARTIAL** | Same as Oracle #13. Described as "headless server" but first-boot requirement not explicit. |
| M4 | mDNS rate limiting not applied | **✅ VERIFIED** | `nftables.conf:20`: `limit rate 10/second`. |
| M5 | GPU Hot PyPI availability | **⚠️ PARTIAL** | `04-install-python-apps.chroot:10`: `pip install gpu-hot`. Whether `gpu-hot` exists on PyPI cannot be verified from code alone. |
| M6 | Upgrade path not documented | **✅ VERIFIED** | `docs/user-guide/src/admin/updating.md`. |
| M7 | Missing system-api user | **✅ VERIFIED** | `01-setup-system.chroot:10`: creates `neuraldrive-api` user. `neuraldrive-system-api.service:6`: `User=neuraldrive-api`. |

**Score: 19/23 VERIFIED, 4 PARTIAL (including 2 N/A)**

---

## Summary

| Section | Total | ✅ Verified | ⚠️ Partial | ❌ Not Addressed | N/A |
|---|---|---|---|---|---|
| Review 1: Feasibility | 10 | 8 | 1 | 0 | 1 |
| Review 2: Security | 9 | 6 | 1 | 3 | 0 |
| Review 3: UX | 10 | 4 | 4 | 2 | 0 |
| Cross-Cutting | 10 | 10 | 0 | 0 | 0 |
| Oracle Review | 8 | 5 | 2 | 1 | 0 |
| Review 4: Blocking | 8 | 8 | 0 | 0 | 0 |
| Review 4: Significant | 8 | 7 | 1 | 0 | 0 |
| Review 4: Minor | 7 | 4 | 2 | 0 | 1 |
| **TOTAL** | **70** | **52** | **11** | **6** | **2** |

---

## Next Steps: Items NOT ADDRESSED (6)

These items have no corresponding implementation and would need new work:

1. **Sec-Med-6 — CORS headers**: Add CORS configuration to Caddyfile for browser-based API clients from other origins.
2. **Sec-Low-8 — Intrusion detection docs**: Document AIDE or rkhunter as optional add-ons for persistent installations.
3. **Sec-Low-9 — Log injection**: Add structured JSON audit logging with sanitization of user-supplied data (model names) in the System API.
4. **UX-4 / Oracle-17 — CD mode messaging**: Read `/run/neuraldrive/media.conf` in the TUI and display user-friendly messaging when `NEURALDRIVE_IS_CD=true` (e.g., "You booted from CD. To download models, connect a USB drive or reboot from USB.").
5. **UX-6 — Model recommendations**: Have the wizard read `neuraldrive-models.yaml` and detected GPU/RAM info to recommend models during step 5 (e.g., "Your RTX 4090 has 24GB VRAM. Recommended: llama3.1:70b-q4").

## Next Steps: Items PARTIALLY ADDRESSED (11)

These items have partial implementations that could be improved:

1. **Rev1-4 — Pin Open WebUI version**: Change `pip install open-webui` to `pip install open-webui==X.Y.Z` in `04-install-python-apps.chroot`.
2. **Sec-Med-5 — Credential ownership**: Change credentials.conf to `root:neuraldrive-admin` with mode 640 for explicit privilege separation.
3. **UX-3 — LUKS encryption in wizard**: Decide whether to add a LUKS step to the wizard or document its absence as intentional.
4. **UX-5 / Oracle-18 — Single-port API**: Consider routing `/api/*` through port 443 in addition to 8443 so a single URL works for everything.
5. **UX-8 — Printable quick-start**: Create a one-page printable card version of the quick-start guide.
6. **UX-10 — Service operation spinners**: Add loading spinners to service start/stop/restart actions in the TUI services screen.
7. **S1 — Document sentinel files**: Add code comments explaining why `initialized` and `first-boot-complete` are separate sentinels.
8. **Oracle-13 / M3 — Headless constraint**: Add explicit documentation: "A local keyboard and monitor are required for the first-boot wizard. After initial setup, all management can be done remotely."
9. **M5 — Verify gpu-hot on PyPI**: Confirm that `gpu-hot` is a real PyPI package, or replace with an alternative GPU monitoring library.
