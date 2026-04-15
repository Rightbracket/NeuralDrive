*This chapter is for everyone.*

# Model Management via TUI

The Model Management screen allows you to download, unload, and delete LLMs directly from the terminal. Access this screen by pressing **M** from the main dashboard.

## Models Screen Interface

```text
┌──────────────── Model Management ────────────────────────────┐
│ NAME                SIZE    STATUS      ACTION               │
│ llama3.1:8b        4.7GB   LOADED      [U]nload  [D]elete   │
│ codestral:latest   8.2GB   LOADED      [U]nload  [D]elete   │
│ mistral:7b         4.1GB   CACHED      [L]oad    [D]elete   │
├──────────────────────────────────────────────────────────────┤
│ [P]ull Model  [I]mport GGUF  [B]ack                         │
└──────────────────────────────────────────────────────────────┘
```

## Available Actions

Each model in the list supports specific actions based on its current state:

- **[L]oad:** If a model is **CACHED** (on disk but not in memory), pressing **L** will trigger a load into VRAM.
- **[U]nload:** If a model is **LOADED**, pressing **U** will eject it from VRAM. This is useful if you want to free up space for a different model manually.
- **[D]elete:** Pressing **D** will prompt for confirmation and then remove the model weights and metadata from the persistent storage.

## Pulling New Models

To download a new model from the Ollama registry:

1. Press **P** (Pull Model).
2. Enter the full model string (e.g., `llama3.1:8b`).
3. Press Enter to start the download.
4. A progress bar will appear in the action column. You can press **Esc** or **Q** to cancel the download at any time.

## Importing GGUF Files

If you have a GGUF file on an external device or elsewhere in the filesystem, you can import it by pressing **I** (Import GGUF).

1. Provide the absolute path to the `.gguf` file.
2. NeuralDrive will create a local manifest and copy the file into the internal model storage area.
3. Once imported, the model will appear in your list with a default name derived from the filename.

Press **B** or **Back** to return to the main dashboard.

