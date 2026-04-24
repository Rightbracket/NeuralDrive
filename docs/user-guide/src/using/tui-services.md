*This chapter is for everyone.*

# Service Control

The Services screen provides a centralized interface for managing the background system processes that power NeuralDrive.

## Access
Press **F3** from any screen to access Service Control.

## Layout
The screen displays a scrollable list of services. Each service is represented by a `ServiceItem` widget showing the service name, its current status, and a set of action buttons.

### Services Managed
The TUI allows you to manage critical NeuralDrive components, including:
- `neuraldrive-ollama`: The core model execution engine.
- `neuraldrive-webui`: The browser-based user interface.
- Any other configured system services specific to the NeuralDrive distribution.

## Navigation
- **Up / Down arrows**: Navigate between the different services in the list.
- **Left / Right arrows**: Navigate between the action buttons (Start/Stop/Restart) for the currently selected service. The focus will automatically skip buttons that are disabled based on the service's current state.
- **Enter**: Activate the focused action button.

## Action Buttons
Each service has three colored action buttons that enable or disable dynamically:

- **Start** (green): Starts a service that is currently stopped or inactive.
- **Stop** (red): Gracefully shuts down a running service.
- **Restart** (amber): Stops and immediately restarts a running service. This is often the quickest way to resolve minor connectivity or performance issues.

## Auto-Refresh and Monitoring
The status of all services is automatically polled every 5 seconds to ensure the interface reflects the actual state of the system. 

If a service like `neuraldrive-ollama` shows a failed or inactive status, use the action buttons to restore it. Continuous monitoring and manual control through this screen help maintain the overall health of your NeuralDrive instance.
