*This chapter is for contributors and maintainers.*

# live-build Overview

`live-build` is a set of scripts used to create Debian Live system images. It is the core framework used by NeuralDrive to generate its bootable ISO files.

## How live-build Works

The `live-build` process is divided into several stages, each responsible for a different part of the system creation:

1. **Bootstrap**: Downloads a minimal Debian base system using `debootstrap`.
2. **Chroot**: Enters the base system and installs additional packages, executes hooks, and applies configurations.
3. **Binary**: Packages the chroot into a SquashFS image and creates the final bootable medium (ISO or HDD image).
4. **Source**: (Optional) Creates a source image containing the source code for all packages used.

## Configuration Logic

The behavior of `live-build` is controlled by the contents of the `config/` directory. When you run `lb config`, these files are read to generate a master configuration for the build.

### Key Directories
- `config/package-lists/`: Defines which packages are installed from the Debian repositories.
- `config/includes.chroot/`: Files placed here are copied directly into the chroot filesystem before it is packed.
- `config/hooks/`: Executable scripts that run inside the chroot to perform complex setup tasks.
- `config/archives/`: Custom repository definitions and GPG keys.

## NeuralDrive Implementation

NeuralDrive extends the standard `live-build` workflow with a custom wrapper (`build.sh`). This wrapper handles pre-build tasks like validating the environment and post-build tasks like branding the ISO.

### Build Stages in NeuralDrive
1. **Pre-Configuration**: Setting version strings and updating model metadata.
2. **Standard live-build Workflow**: Running `lb clean`, `lb config`, and `lb build`.
3. **Artifact Management**: Moving the finished ISO to the `output/` directory and generating checksums.

## Benefits of live-build

- **Reproducibility**: The same configuration produces the same image every time.
- **Flexibility**: Easily switch between different Debian branches (Stable, Testing, Sid).
- **Automation**: The entire process can be run in a CI/CD environment without manual intervention.

For official documentation on `live-build`, refer to the [Debian Live Manual](https://live-team.pages.debian.net/live-manual/).

