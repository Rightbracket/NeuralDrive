*This chapter is for everyone.*

# Web Dashboard

NeuralDrive's web-based interface consists of two applications: the main Chat Dashboard and the administrative System Panel. Both are accessible through your local network.

## Accessing the Dashboard

Once your server is booted and configured, navigate to the following URL in your web browser:
`https://<SERVER_IP>/` or `https://neuraldrive.local/`

NeuralDrive uses a secure Caddy web server to proxy all traffic over port 443. Login using the administrator credentials created during the [First Boot](../getting-started/first-boot.md) wizard.

## Chat Dashboard (Open WebUI)

The primary interface for NeuralDrive is Open WebUI. It provides a robust environment for managing and interacting with large language models. Key features include:

- **Model Management:** Download, update, and switch between various models.
- **RAG Integration:** Upload documents to use as context for your conversations.
- **Multi-user Support:** Admins can create and manage additional user accounts. Registration is disabled by default for security (`ENABLE_SIGNUP=false`).
- **Custom Branding:** The interface is pre-configured with NeuralDrive branding and dark mode.

## System Panel

For hardware monitoring and service management, NeuralDrive includes a custom System Panel. This FastAPI application runs separately from the chat interface.

- **Main System Panel:** `https://<SERVER_IP>:8443/system/`
- **GPU Monitoring:** `https://<SERVER_IP>:8443/monitor/`

The System Panel provides real-time data on your hardware performance, thermal status, and running services. This separation ensures that even if a heavy inference task impacts the Chat Dashboard, you can still monitor your hardware health.

## Two-Application Architecture

NeuralDrive uses a dual-app architecture to balance user interaction and system reliability:
1. **Open WebUI:** Dedicated to chat, models, and user management.
2. **System Panel:** Dedicated to low-level hardware monitoring and service health.

This design allows for maximum uptime and precise control over your local inference environment.

Next step: [Chat Interface](chat.md)
