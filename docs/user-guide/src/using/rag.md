*This chapter assumes familiarity with RAG concepts.*

# Retrieval-Augmented Generation (RAG)

Retrieval-Augmented Generation (RAG) is a technique that allows an LLM to access and reference specific information from your own documents during a conversation. This effectively gives the model "long-term memory" and access to data it wasn't originally trained on.

## How RAG Works in NeuralDrive

When you upload a document, NeuralDrive processes it through several steps:
1. **Parsing:** The text is extracted from the file (PDF, TXT, DOCX, etc.).
2. **Chunking:** The text is broken down into smaller, manageable pieces.
3. **Embedding:** Each chunk is converted into a numerical vector that represents its semantic meaning.
4. **Storage:** These vectors are stored in a local vector database on your persistent partition.

When you ask a question in a RAG-enabled chat, the system searches the vector database for chunks that are mathematically similar to your query and provides them to the LLM as context.

## Using RAG in Conversations

To use your documents in a chat:

1. **Upload Documents:** Use the **Documents** page in the Open WebUI to upload your files.
2. **Select for Chat:** In the chat interface, you can select specific documents or entire collections to be used as context for your current session.
3. **Querying:** Simply type your question. The model will analyze the provided document context and generate a response based on those facts.

## Limitations on LiveUSB

While RAG is a powerful feature, there are important considerations when running from a LiveUSB:

- **Processing Power:** Embedding large documents is a CPU and GPU intensive task. Processing a hundreds-of-pages PDF may take several minutes.
- **Persistence:** Ensure your documents are stored on the persistence partition if you want them to remain available after a reboot.
- **Storage Space:** Vector databases can grow significantly in size. Monitor your [Storage Management](../models/storage.md) closely if you plan to index large libraries of documents.

