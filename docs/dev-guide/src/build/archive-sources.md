*This chapter is for contributors and maintainers.*

# Archive Sources

NeuralDrive supplements the standard Debian repositories with third-party archives to provide the latest GPU drivers and specialized software. These are managed via the `config/archives/` directory.

## Repository Configuration

Each third-party archive requires two files:
1. **`.list` file**: Defines the repository URL and components (e.g., `deb https://repo.radeon.com/rocm/apt/latest focal main`).
2. **`.key` file**: The GPG public key used to verify the packages in the repository.

## Currently Configured Archives

### Debian Backports
Used to pull newer versions of certain packages (like the Linux kernel) while remaining on the Stable (Bookworm) base. Configured in `config/archives/backports.list.chroot`.

### NVIDIA CUDA Repository
Provides the proprietary NVIDIA driver. Required because Debian bookworm only carries the 535 branch (max CUDA 12.2), which cannot load the CUDA 12.8 kernel images shipped by current Ollama releases — the failure mode is `CUDA error: device kernel image is invalid`. Configured in `config/archives/nvidia-cuda.{list,key,pref}.chroot`.

The pin file (`nvidia-cuda.pref.chroot`) locks the headless driver stack to **570.133.20-1**, the last 570.x build whose `nvidia-kernel-dkms` is satisfied by Debian bookworm's `dkms` (3.0.10). Versions from 570.148.08 onward require `dkms >= 3.1.8` and would fail to install. All non-driver packages from the NVIDIA repo are pinned at low priority so they cannot accidentally replace unrelated Debian packages.

## Repository Pinning

Third-party repositories must not be allowed to upgrade core Debian packages by accident. APT pinning is configured per archive in `config/archives/*.pref.chroot`.

The NVIDIA pin uses three rules in `nvidia-cuda.pref.chroot`:

```text
# Driver packages: from NVIDIA repo at highest priority
Package: nvidia-* libnvidia-* libcuda* libcudadebugger* libnvcuvid* libnvoptix* firmware-nvidia-*
Pin: origin "developer.download.nvidia.com"
Pin-Priority: 1001

# Lock the branch to 570.133.20 (dkms 3.0.10 compatibility)
Package: nvidia-kernel-dkms nvidia-driver-cuda ...
Pin: version 570.133.20*
Pin-Priority: 1001

# Everything else from the NVIDIA repo at low priority
Package: *
Pin: origin "developer.download.nvidia.com"
Pin-Priority: 100
```

## Adding a New Archive

To add a new repository:
1. Download the GPG key and place it in `config/archives/repo-name.key`.
2. Create a list file at `config/archives/repo-name.list.chroot`.
3. (Optional) Create a preferences file at `config/archives/repo-name.pref.chroot` if pinning is required.

> **Warning**: Be cautious when adding third-party archives. Every new source increases the risk of package conflicts and can significantly increase the size of the final ISO image. Always verify the authenticity of GPG keys before adding them to the project.

