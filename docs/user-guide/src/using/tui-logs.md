*This chapter is for everyone.*

# System Logs

The System Logs screen provides a real-time view of internal events and service outputs. This is an essential tool for diagnosing issues with model loading, network connectivity, or user authentication. Access this screen by pressing **L** from the main dashboard.

## Logs Screen Interface

```text
┌──────────────── System Logs ─────────────────────────────────┐
│ Service: [All Services] │ Level: [Info+] │ Search: [        ]│
├──────────────────────────────────────────────────────────────┤
│ 10:15:30 [OLLAMA] Loaded llama3.1:8b successfully            │
│ 10:15:35 [WEBUI] Admin user logged in from 192.168.1.5       │
│ 10:16:12 [OLLAMA] Error: Connection closed by remote peer    │
├──────────────────────────────────────────────────────────────┤
│ [S]elect Service  [F]ilter  [C]lear  [B]ack                 │
└──────────────────────────────────────────────────────────────┘
```

## Filtering and Navigation

The logs can be voluminous, so the TUI provides several ways to narrow down the information:

- **S (Select Service):** Cycles through specific services (e.g., OLLAMA, WEBUI, SYSTEM) or displays all services combined.
- **F (Filter):** Adjusts the minimum severity level of logs displayed (e.g., Info, Warning, Error).
- **Search:** Allows you to type a keyword to highlight or filter lines containing that string.
- **C (Clear):** Clears the current view of logs. Note that this does not delete the logs from the disk, only from the current TUI session.

## Understanding Log Entries

Each log entry includes a timestamp, the source service name in brackets, and the message content.

- **[OLLAMA]:** Records model pull progress, loading/unloading events, and inference errors.
- **[WEBUI]:** Tracks user logins, API requests, and document processing events.
- **[SYSTEM]:** General OS-level events, including disk space warnings and network changes.

If you encounter an error you don't understand, the specific message provided in the logs is the most useful piece of information to include in a support request or bug report.

Press **B** or **Back** to return to the main dashboard.

