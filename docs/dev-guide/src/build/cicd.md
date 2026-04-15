*This chapter is for contributors and maintainers.*

# CI/CD Pipeline

NeuralDrive uses GitHub Actions to automate the testing, building, and distribution of system images.

## Workflow Structure

The primary workflow is defined in `.github/workflows/build.yml`. It consists of several jobs that run in sequence.

### 1. Lint and Test
- Runs `shellcheck` on all scripts in `config/hooks/` and `scripts/`.
- Runs `ruff` on the Python codebase.
- Executes the `pytest` suite for the System API.
- This job runs on every push and pull request.

### 2. Build Matrix
When a change is merged into `main` or a tag is created, the build job is triggered. It uses a matrix to build multiple variants of NeuralDrive simultaneously:
- **Full**: Includes drivers for NVIDIA, AMD, and Intel.
- **NVIDIA-Only**: Optimized for NVIDIA hardware.
- **Minimal**: CPU-only, intended for testing and low-power hardware.

### 3. Artifact Publishing
Finished ISO images are uploaded as GitHub Action artifacts. For tagged releases, the workflow also:
- Generates SHA256 checksums.
- Signs the checksums using the project's GPG key.
- Creates a new GitHub Release and uploads the ISOs and signatures.

## Configuration (neuraldrive-build.yaml)

The CI pipeline can be configured via a `neuraldrive-build.yaml` file in the repository root. This allows maintainers to:
- Toggle specific build variants.
- Define which models are pre-loaded into the images.
- Set custom version strings for nightlies.

## Runner Requirements

Building ISO images requires a Linux runner with support for nested virtualization or privileged containers. We use large GitHub-hosted runners to ensure there is enough disk space and CPU power to complete builds within the 60-minute timeout.

## Automated Testing in CI

In addition to static analysis, the CI pipeline attempts a "Dry Run" build:
- It runs `lb config` to verify the configuration is valid.
- It performs the bootstrap stage to ensure the Debian repositories are accessible.
- Full binary builds are only performed on the `main` branch to conserve resources.

> **Note**: Because CI runners do not have physical GPUs, we cannot perform full GPU validation in the cloud. These tests remain a manual requirement for the release checklist.

