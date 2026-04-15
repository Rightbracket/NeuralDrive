*This chapter assumes Linux system administration experience.*

# Pre-loading Models

For large-scale deployments or specialized air-gapped environments, you may want to distribute NeuralDrive images that already contain specific models. This avoids the need for users to download gigabytes of data on first boot.

## Why Pre-load?

- **Zero-Setup Experience:** Users can start chatting immediately without internet access.
- **Consistent Environment:** Ensures every instance of your custom NeuralDrive image has the exact same model versions.
- **Reduced Bandwidth:** Saves significant time and network resources during mass deployments.

## Build Configuration

Pre-loading is managed through the `neuraldrive-build.yaml` configuration file used during the image creation process. You can specify a list of models to be included in the `models.preload` section.

```yaml
models:
  preload:
    - llama3.1:8b
    - phi3:mini
    - qwen2.5:3b
```

## Two-Phase Build Approach

The current build system uses a two-phase approach to ensure models are correctly staged and compressed within the squashfs filesystem of the LiveUSB.

1. **Phase 1: Environment Staging.** The build system sets up the base operating system and installs the Ollama service.
2. **Phase 2: Model Injection.** In this phase, the build system pulls the requested models from the official Ollama registry into a temporary staging directory.

Currently, this injection is a manual staging step during the development of custom images. You must ensure that the staging environment has internet access to perform the initial `ollama pull` commands before the final image is wrapped.

## Model Persistence

It is important to note that models pre-loaded into the base image are stored in the read-only section of the drive. While they are available for use immediately, any new models downloaded by the user after booting will be stored in the `/var/lib/neuraldrive/models/` directory on the persistence partition.

For more information on customizing your NeuralDrive build, refer to the [Custom Images](../customization/custom-images.md) documentation.

