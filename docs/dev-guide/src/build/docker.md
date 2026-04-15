*This chapter is for contributors and maintainers.*

# Docker Build Environment

The Docker-based build environment provides a consistent, isolated workspace for generating NeuralDrive images regardless of the host operating system.

## Dockerfile Walkthrough

The `Dockerfile` in the project root defines the builder image. It is based on `debian:bookworm` to match the target OS.

Key components of the Dockerfile:
- **Base Layer**: Installs `live-build`, `debootstrap`, and other core utilities.
- **Workdir**: Sets `/build` as the working directory.
- **Volume**: Declares `/output` as a destination for the finished ISO.
- **Entrypoint**: A script that runs `lb clean`, `lb config`, and `lb build` in sequence.

## Docker Compose Configuration

The `docker-compose.yml` simplifies the process of launching the builder with the correct permissions and mounts.

```yaml
services:
  builder:
    build: .
    privileged: true
    volumes:
      - .:/build
      - ./output:/output
    environment:
      - BUILD_VARIANT=full
```

### Privileged Mode
The `privileged: true` flag is mandatory. `live-build` uses `chroot`, `mount`, and `mknod`, all of which require elevated privileges. Additionally, generating SquashFS and ISO images requires access to the host's loop devices.

## Building with Docker

To start a build:
```bash
docker compose run --rm builder
```

The finished ISO will appear in the `./output/` directory on your host machine.

## Benefits and Limitations

### Benefits
- **No Host Contamination**: Build dependencies are not installed on your primary OS.
- **Cross-Platform**: Build from macOS or Windows (using Docker Desktop).
- **CI Readiness**: The same Docker image used for local development is used in GitHub Actions.

### Limitations
- **Performance**: Building inside a container can be slightly slower due to I/O overhead on non-Linux hosts.
- **Loop Device Contention**: If multiple builds are run simultaneously on the same host, they may compete for the same loop devices, leading to failures.

> **Tip**: If you encounter "Permission Denied" errors when accessing the `./output/` directory on Linux, ensure that your user has permission to write to that folder, as files created by the root user inside the container may have restricted permissions on the host.

