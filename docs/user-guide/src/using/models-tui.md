*This chapter is for everyone.*

# Model Management via TUI

The Model Management screen allows you to download, load, unload, and delete LLMs directly from the terminal.

## Access
Press **F2** from any screen to access Model Management.

## Layout
The screen is organized into three zones that you can navigate between using **Tab** or **Shift+Tab**:

1.  **Installed Models list** (top zone): A scrollable list of models currently on your system.
2.  **Browse Catalog** button (middle zone): Opens a popup to browse the Ollama library.
3.  **Pull by name** (bottom zone): A text input field and a **Pull** button for direct model downloads.

### Installed Models List
Each model in the list displays its details in a columnar format. A legend header with `/` separators appears above the list:
`Model name | Params | Quant | Disk | VRAM | Status`

- **Model name**: The name of the model (e.g., `llama3:8b`).
- **Params**: Parameter count of the model.
- **Quant**: Quantization level.
- **Disk**: Space occupied on disk.
- **VRAM**: Measured or cached VRAM usage (e.g., "6.2 GB" or "~6.2 GB").
- **Status**: Current state of the model ("loaded (GPU)", "loaded (CPU)", or "ready").

## Navigation
- **Tab / Shift+Tab**: Cycle focus between the three zones (models → browse → pull-input → pull-btn).
- **Up / Down arrows**: Navigate through the installed model list. The view scrolls automatically to follow your focus.
- **Left / Right arrows**: Navigate between the action buttons (Load/Unload/Delete) for the currently selected model. The cursor automatically skips disabled buttons.
- **Enter**: Activate the focused button or zone.
- **PageUp / PageDown**: Fast scroll through the model list.

## Model Actions
Each model has specific action buttons:

- **Load**: Loads the model into VRAM for inference. The status will show "Loading..." while in progress. Loaded models use a `keep_alive: -1` setting for infinite retention.
- **Unload**: Removes the model from VRAM. The system polls the engine until the unload is confirmed.
- **Delete**: Permanently removes the model from disk. A confirmation prompt will appear before deletion.

## Downloading Models

### Browse Catalog
Selecting the **Browse Catalog** button opens a scrollable popup listing popular models from the Ollama library. Select a model from the list and confirm to start the download.

### Pull by Name
To download a specific model, type its name (e.g., `llama3:8b`) into the text input field in the bottom zone and press **Enter** or click the **Pull** button. 

A progress bar will show the download status. You can press **Escape** or the **Cancel** button to abort an active download.

## VRAM Management
VRAM usage values are measured during operation or retrieved from a cache stored in `/var/lib/neuraldrive/config/`. 

Multiple models can be installed and loaded simultaneously. The underlying engine manages VRAM using an LRU (Least Recently Used) eviction policy when the `OLLAMA_MAX_LOADED_MODELS` setting is set to auto.
