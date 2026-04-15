*This chapter is for everyone.*

# Model Management via Web

The Open WebUI provides a rich, graphical interface for managing your LLMs. This is the recommended method for most users who are connected to the NeuralDrive network.

## Accessing the Models Page

Once logged into the Open WebUI, you can find the model management tools in the settings or administration area, typically under a **Models** tab.

## Viewing Downloaded Models

The Models page displays a list of all models currently stored on your NeuralDrive. For each model, you can see:

- **Name and Tag:** (e.g., `llama3.1:8b`)
- **Size:** The disk space occupied by the model.
- **Quantization:** The precision level of the weights.
- **Last Used:** When the model was last loaded for a conversation.

## Pulling New Models

To download a new model from the official registry:

1. Locate the input field titled "Pull a model from Ollama.com".
2. Enter the model string (e.g., `mistral:7b`).
3. Click the download/pull button.
4. A progress bar will appear. You can navigate away from the page, and the download will continue in the background.

## Deleting Models

If you need to free up storage space:

1. Find the model you wish to remove in the list.
2. Click the trash can or delete icon associated with that model.
3. Confirm the deletion when prompted.

Note that deleting a model from the web UI is permanent and removes the files from the `/var/lib/neuraldrive/models/` directory.

## Model Details and Customization

Clicking on an individual model in the list allows you to view more detailed metadata, including the Modelfile used to create it. Advanced users can use this interface to create "Model Files" which are customized versions of base models with specific system prompts or parameters (like temperature and top-k) pre-configured.

