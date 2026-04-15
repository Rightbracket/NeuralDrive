*This chapter is for contributors and maintainers.*

# Running Tests

NeuralDrive includes a suite of automated and manual tests to ensure system stability across different hardware targets.

## Boot Testing with QEMU

Before flashing to physical hardware, use QEMU to verify that the ISO image boots to the TUI login screen.

```bash
./scripts/test-boot.sh build/neuraldrive-dev.iso
```

This script launches a virtual machine with:
- 8GB of RAM
- UEFI boot support
- A virtual disk for testing persistence
- Port forwarding for the System API (3001) and WebUI (443)

## GPU Validation

Because QEMU does not easily simulate a physical GPU, vendor-specific detection and inference tests must be run on real hardware.

### Automatic Detection Test
```bash
sudo /usr/lib/neuraldrive/gpu-detect.sh
```
This should correctly identify the active GPU and generate `/run/neuraldrive/gpu.conf` with the appropriate vendor tags.

### Inference Verification
The `scripts/test-gpu.sh` utility performs a small inference task to verify that the Ollama service can communicate with the GPU drivers and load a model into VRAM.

## API and Integration Testing

The System API is tested using `pytest`. These tests verify that the FastAPI endpoints correctly interact with systemd and the underlying config files.

```bash
# From the project root with the venv active
pytest tests/test_api.py
```

These tests cover:
- Authentication token verification
- Service status reporting
- Log retrieval
- Network configuration changes

## CI Integration

Every Pull Request triggers a subset of these tests via GitHub Actions:
1. **Linting**: ShellCheck for scripts and Ruff for Python code.
2. **Unit Tests**: Running the API test suite against a mock system.
3. **Build Test**: Attempting to run `lb config` and a partial `lb build` to catch configuration errors.

> **Note**: Full ISO builds and QEMU boot tests are typically reserved for merges into the `main` branch due to their long execution time.

