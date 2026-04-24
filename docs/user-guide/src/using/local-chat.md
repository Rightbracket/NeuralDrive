*This chapter is for everyone.*

# Local Terminal Chat

For quick testing and offline interaction, NeuralDrive includes a lightweight, terminal-based chat interface. This allows you to communicate with your local models without needing a web browser or a network connection.

## Launching the Chat

Access the local chat by pressing **F5** from any screen.

## Using the Chat Interface

1. **Model Selection:** A model selector dropdown at the top of the screen lets you choose which installed model to chat with. The selected model persists even when switching away and returning to the chat screen.
2. **Messaging:** Type your message into the input field at the bottom of the screen. Press Enter to send.
3. **Streaming Responses:** The model's response will stream directly into the terminal window in real-time.
4. **Keyboard Shortcuts:**
   - **F1-F4:** Switch to another TUI screen (Dashboard, Models, Services, or Logs).
   - **Ctrl+C:** Interrupt the current response generation.

## Features and Limitations

The TUI chat is designed for simplicity and speed. You must have at least one model downloaded and loaded to use the chat interface.

- **Fast & Lightweight:** Minimal resource overhead compared to the full web UI.
- **Persistent Context:** The chat maintains a basic conversation history within the current session, allowing for follow-up questions.
- **Streaming:** Responses appear as they are generated, providing immediate feedback.

**Limitations compared to the Web UI:**
- **No Multimedia:** Does not support images, file uploads, or complex markdown rendering.
- **Single Session:** Conversation history is not saved across TUI restarts.
- **No RAG:** The local chat cannot access your uploaded documents; for Retrieval-Augmented Generation, use the [Web Interface](../using/models-web.md) or refer to the [RAG chapter](../using/rag.md).

