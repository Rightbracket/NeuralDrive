*This chapter is for everyone.*

# Downloading Models

NeuralDrive provides four primary methods for downloading and managing LLMs. Regardless of the method used, all models are stored in a central location on the persistent partition of your drive.

## 1. Web Interface (Open WebUI)

The most user-friendly method is through the Open WebUI.

- Navigate to the **Models** page in the web interface.
- Enter the name of the model you wish to pull (e.g., `llama3.1:8b`).
- Click the download icon.
- You can monitor the download progress directly in the web UI.

## 2. Terminal User Interface (TUI)

The TUI provides a fast, keyboard-driven way to manage models without opening a browser.

- From the main dashboard, press **M** to enter the Models screen.
- Press **P** to initiate a Pull Model command.
- Enter the model string and press Enter.
- The TUI displays a progress bar and allows you to cancel if needed.

## 3. Command Line Interface (CLI)

For power users and automated scripts, you can use the Ollama CLI directly from any terminal session.

```bash
ollama pull <model_name>
```

Example:
```bash
ollama pull qwen2.5:3b
```

## 4. API Request

NeuralDrive's underlying Ollama service exposes an API that can be used to programmatically trigger downloads.

```bash
curl -X POST http://localhost:11434/api/pull -d '{"name": "phi3:mini"}'
```

## Storage Location and Progress

All model data is stored in the following path on the persistence partition:
`/var/lib/neuraldrive/models/`

Specifically:
- **Blobs:** Actual model weights are stored in `/var/lib/neuraldrive/models/blobs/`.
- **Manifests:** Metadata about the models is stored in `/var/lib/neuraldrive/models/manifests/`.

When a download is in progress, NeuralDrive tracks the state and prevents simultaneous downloads of the same model. If a download is interrupted, it can typically be resumed by initiating the pull command again. Ensure you have sufficient disk space before starting a large download by checking the [Storage Management](../models/storage.md) guide.

