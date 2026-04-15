*This chapter is for contributors and maintainers.*

# Test Strategy

NeuralDrive uses a multi-layered testing strategy to ensure that the appliance is stable across a wide variety of hardware and software configurations.

## Test Philosophy

We prioritize integration testing over unit testing. Since NeuralDrive is a system appliance, its stability depends on the interaction between the kernel, drivers, systemd, and the application stack.

### Key Principles
- **Reproducibility**: Tests should yield the same results given the same ISO image and virtualized environment.
- **Automation**: Wherever possible, tests should run in the CI pipeline without manual intervention.
- **Hardware Diversity**: While CI handles basic logic, manual "Target Hardware" testing is mandatory for every release.

## Test Categories

### 1. Boot Testing
Ensures the ISO image is correctly formatted and can boot to a functional state. This is primarily handled via QEMU.

### 2. Hardware and GPU Testing
Validates that `gpu-detect.sh` correctly identifies hardware and that the appropriate compute stack (CUDA, ROCm, OneAPI) is loaded. This must be done on physical hardware.

### 3. API Testing
Verifies the endpoints of the System API and the Ollama inference API. These tests ensure that the core logic of the appliance is working as expected.

### 4. Security Auditing
Periodic checks of service isolation, systemd hardening, and firewall rules. This involves running automated security scanners against the running appliance.

## The Test Life Cycle

1. **Local Development**: Developers run unit tests and QEMU boot tests.
2. **Pull Request**: CI runs linting, API tests, and build validation.
3. **Pre-Release**: Maintainers perform full ISO builds and verify them on a variety of target hardware.
4. **Post-Release**: Community feedback and bug reports are triaged and integrated back into the test suite.

> **Note**: For detailed instructions on running specific tests, refer to the subsequent chapters in this section.

