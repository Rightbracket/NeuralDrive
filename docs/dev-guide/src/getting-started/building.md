*This chapter is for contributors and maintainers.*

# Building from Source

NeuralDrive uses a customized `live-build` workflow to generate its bootable ISO images. The build process can be initiated either natively on a Debian system or through a Docker container.

## Standard Build Process

The primary entry point for building is the `build.sh` script located in the project root.

### Native Build
To start a build on a native Debian host:
```bash
sudo ./build.sh
```

### Docker Build
If you prefer using Docker, use the provided compose configuration:
```bash
docker compose up builder
```
The Docker method uses `privileged: true` and mounts the current directory into the container to allow the build system to interact with kernel loop devices.

## Build Stages

The `build.sh` script coordinates several distinct phases:
1. **Validation**: Checks that the host environment has all necessary tools and that configuration files are valid.
2. **Configuration**: Runs `lb config` to set up the live-build environment based on parameters in the `config/` directory.
3. **Branding**: Applies NeuralDrive-specific themes, splash screens, and versioning info.
4. **Model Staging**: Downloads base models defined in `neuraldrive-models.yaml` so they can be baked into the image (if configured).
5. **Chroot Construction**: Downloads the Debian base and installs packages listed in `config/package-lists/`.
6. **Hook Execution**: Runs the scripts in `config/hooks/normal/` to configure services and user accounts.
7. **Binary Stage**: Packs the filesystem into a SquashFS image and generates the final ISO.

## Incremental Builds and Cleanup

Building the entire system from scratch can take between 30 and 90 minutes depending on your internet connection and CPU speed.

To reset the build environment and start fresh:
```bash
sudo lb clean --all
```

> **Warning**: Avoid manually deleting files in the `chroot/` directory, as this can leave stale mount points on your host system. Always use `lb clean`.

## Common Build Errors

- **Loop Device Exhaustion**: If the build fails during the binary stage, you may have run out of available loop devices. Run `losetup -a` to check and reboot the host if necessary.
- **GPG Errors**: Failures during the archive staging usually indicate a missing or expired repository key in `config/archives/`.
- **Space Requirements**: Ensure you have at least 40GB of free space before starting a build, as the chroot and temporary SquashFS files are large.

The final output will be located in the `build/` directory as a `.iso` file.

