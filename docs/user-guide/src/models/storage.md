*This chapter is for everyone.*

# Storage Management

Because LLMs can be several gigabytes in size, managing disk space is essential for a stable NeuralDrive experience. All models are stored on the persistent partition of your drive.

## Checking Available Space

You can monitor your disk usage through three primary interfaces:

1. **TUI Dashboard:** The main screen shows current disk usage as a percentage and in GB.
2. **Web System Panel:** The Open WebUI administration area provides a graphical view of storage consumption.
3. **Command Line:** You can run the following command from any terminal to see exactly how much space remains on the persistence partition:
   ```bash
   df -h /var/lib/neuraldrive
   ```

## Storage Thresholds

NeuralDrive monitors storage levels and will alert you when space is running low.

- **80% Usage (Warning):** A warning badge appears in the TUI and web interface. You should consider deleting unused models.
- **90% Usage (Critical):** System performance may degrade. Urgent action is required to free space.
- **95% Usage (Blocked):** Downloads are automatically blocked to prevent the system from becoming unresponsive.

## Deleting Models

If you need to free up space, you can delete models that are no longer in use.

- **TUI:** Navigate to the **Models** screen (**M**), highlight a model, and press **D** to delete it.
- **Web UI:** Go to the **Models** page and use the delete icon next to the model name.
- **CLI:** Run `ollama rm <model_name>`.

Deleting a model removes both its weights (blobs) and metadata (manifests) from `/var/lib/neuraldrive/models/`.

## Hardware Recommendations for Storage

For the best experience, we recommend using a USB drive with at least 128GB of capacity. This allows you to store multiple large models (like `llama3.1:8b` and `codestral:latest`) while still having room for logs and document storage.

If you find that 128GB is insufficient, you can reinstall NeuralDrive on a larger drive or a high-speed external SSD for even more storage capacity.

