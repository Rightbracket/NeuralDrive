*This chapter is for contributors and maintainers.*

# Release Checklist

The release checklist ensures that every version of NeuralDrive is thoroughly tested and meets our quality standards before being distributed to the public.

## Pre-Build Phase
- [ ] **Changelog**: All changes since the last release are documented in `CHANGELOG.md`.
- [ ] **Version**: The `etc/neuraldrive/version` file is updated.
- [ ] **Dependencies**: Python requirements and system package lists are verified for compatibility.
- [ ] **Documentation**: Developer and User Guides reflect the latest features and architectural changes.

## Build Phase
- [ ] **Clean Build**: `lb clean --all` is run before starting the production build.
- [ ] **Variants**: ISO images for all supported variants (Full, NVIDIA-Only, Minimal) are generated.
- [ ] **Checksums**: SHA256SUMS files are created for all artifacts.

## Testing Phase
- [ ] **QEMU Boot**: All variants successfully boot to the TUI in a virtual environment.
- [ ] **NVIDIA GPU**: Verified functional on at least one GeForce and one professional (A-series) card.
- [ ] **AMD GPU**: Verified functional on at least one ROCm-compatible Radeon card.
- [ ] **Intel GPU**: Verified functional on an Arc GPU (if applicable for the release).
- [ ] **Setup Wizard**: The first-boot experience is tested from start to finish, including persistence encryption.
- [ ] **WebUI & API**: All primary routes respond correctly over HTTPS.

## Distribution Phase
- [ ] **Signing**: The SHA256SUMS file is signed using the project's GPG key.
- [ ] **GitHub Release**: A new release is created with a detailed description and attached artifacts.
- [ ] **Social**: Announcements are posted to the project's Discord, Matrix, and Twitter channels.

## Post-Release Phase
- [ ] **Community Support**: Monitor feedback and report any critical bugs.
- [ ] **Bugfix Releases**: If critical regressions are found, a `.1` or `.2` patch is prepared immediately.

> **Tip**: This checklist is integrated into our GitHub PR template and must be completed by the maintainer before a merge to `main`.

