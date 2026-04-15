*This chapter is for contributors and maintainers.*

# Archive Sources

NeuralDrive supplements the standard Debian repositories with third-party archives to provide the latest GPU drivers and specialized software. These are managed via the `config/archives/` directory.

## Repository Configuration

Each third-party archive requires two files:
1. **`.list` file**: Defines the repository URL and components (e.g., `deb https://repo.radeon.com/rocm/apt/latest focal main`).
2. **`.key` file**: The GPG public key used to verify the packages in the repository.

## Currently Configured Archives

### Debian Backports
Used to pull newer versions of certain packages (like the Linux kernel) while remaining on the Stable (Bookworm) base.

### NVIDIA Repository
Provides the latest proprietary drivers and CUDA toolkit directly from NVIDIA.

### ROCm (AMD)
Provides the Radeon Open Compute stack. We pin this to specific versions to ensure compatibility with Ollama's build requirements.

### Intel OneAPI
Provides the necessary libraries for Intel Arc and Data Center GPUs.

## Repository Pinning

To prevent third-party repositories from accidentally upgrading core Debian packages, we use APT pinning. This is configured in `config/archives/*.pref.chroot` files.

Example pin for the NVIDIA repository:
```text
Package: *
Pin: origin developer.download.nvidia.com
Pin-Priority: 600
```

## Adding a New Archive

To add a new repository:
1. Download the GPG key and place it in `config/archives/repo-name.key`.
2. Create a list file at `config/archives/repo-name.list.chroot`.
3. (Optional) Create a preferences file at `config/archives/repo-name.pref.chroot` if pinning is required.

> **Warning**: Be cautious when adding third-party archives. Every new source increases the risk of package conflicts and can significantly increase the size of the final ISO image. Always verify the authenticity of GPG keys before adding them to the project.

