*This chapter is for everyone.*

# Local Terminal Chat

For quick testing and offline interaction, NeuralDrive includes a lightweight, terminal-based chat interface. This allows you to communicate with your local models without needing a web browser or a network connection.

## Launching the Chat

Access the local chat by pressing **C** from the main TUI dashboard.

## Using the Chat Interface

1. **Model Selection:** Upon entering the chat screen, you will be prompted to select one of the models currently available on your system. Use the arrow keys to highlight a model and press Enter.
2. **Messaging:** Type your message into the input field at the bottom of the screen. Press Enter to send.
3. **Streaming Responses:** The model's response will stream directly into the terminal window in real-time.
4. **Keyboard Shortcuts:**
   - **Esc or B:** Return to the model selection or main dashboard.
   - **Ctrl+C:** Interrupt the current response generation.

## Features and Limitations

The TUI chat is designed for simplicity and speed.

- **Fast & Lightweight:** Minimal resource overhead compared to the full web UI.
- **Persistent Context:** The chat maintains a basic conversation history within the current session, allowing for follow-up questions.
- **Streaming:** Responses appear as they are generated, providing immediate feedback.

**Limitations compared to the Web UI:**
- **No Multimedia:** Does not support images, file uploads, or complex markdown rendering.
- **Single Session:** Conversation history is not saved across TUI restarts.
- **No RAG:** The local chat cannot access your uploaded documents; for Retrieval-Augmented Generation, use the [Web Interface](../using/models-web.md) or refer to the [RAG chapter](../using/rag.md).

