*This chapter is for everyone.*

# Service Control

The Services screen provides a centralized interface for managing the background system processes that power NeuralDrive. Access this screen by pressing **S** from the main dashboard.

## Service List

This screen displays all `neuraldrive-*` services and their current operational status:

- **Active:** The service is running normally.
- **Inactive:** The service is stopped.
- **Failed:** The service encountered an error and crashed.

The primary services you will see are:

- `neuraldrive-ollama`: The model execution engine.
- `neuraldrive-webui`: The browser-based interface.
- `neuraldrive-tui`: The terminal interface itself (restarting this will reload the TUI).
- `neuraldrive-network`: Manages mDNS and hostname settings.

## Managing Services

You can control individual services using the following keybindings after selecting a service from the list:

- **R (Restart):** Stops and immediately restarts the selected service. This is the first step you should take if a component becomes unresponsive.
- **S (Start):** Manages starting a service that is currently inactive or failed.
- **T (Stop):** Gracefully shuts down the selected service.

## Recovery and Troubleshooting

If the Dashboard shows an "Ollama Offline" badge, navigate to the Services screen and check the status of `neuraldrive-ollama`. If it is in a **Failed** or **Inactive** state, use the **S** key to start it or **R** to restart it.

Monitoring service status is critical for maintaining system uptime. If a service repeatedly fails, you should examine the system logs for more detailed error information.

Press **B** or **Back** to return to the main dashboard.

