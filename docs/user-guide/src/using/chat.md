*This chapter is for everyone.*

# Chat Interface

The chat interface is your primary tool for interacting with the AI models running on your NeuralDrive server. It is built to support fluid, real-time conversations.

## Starting a New Conversation

To begin a new chat session, click the "New Chat" button located in the sidebar. This opens a fresh workspace where you can enter prompts and receive responses.

## Selecting a Model

NeuralDrive allows you to choose which model handles your query.

1. Locate the model dropdown menu at the top of the chat interface.
2. Select your desired model from the list of installed options.
3. You can switch models mid-conversation without needing to reload the page or start over.

## Streaming Responses

NeuralDrive features real-time token streaming. As the AI generates a response, the text will appear on your screen immediately. This provides a dynamic experience and allows you to begin reading the output before the complete response is generated.

## Conversation History

Your chat history is automatically saved to your NeuralDrive's persistent storage.

- **Storage Location:** All session data is stored in `/var/lib/neuraldrive/webui/`.
- **Retrieval:** You can access previous conversations from the sidebar at any time.
- **Concurrent Chats:** NeuralDrive supports multiple simultaneous chat sessions, allowing you to manage different tasks or projects independently.

The interface is optimized for high performance, ensuring that even with multiple active sessions, your interaction remains responsive.

For more information on the broader system management, return to the [Web Dashboard](web-dashboard.md) chapter.
