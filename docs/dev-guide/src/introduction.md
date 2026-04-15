*This chapter is for contributors and maintainers.*

# Introduction

Welcome to the NeuralDrive Developer Guide. This documentation provides a deep technical look at the internals of NeuralDrive, a headless Large Language Model (LLM) appliance built on Debian 12.

NeuralDrive is designed to transform standard hardware into a high-performance AI server with minimal configuration. It combines modern LLM runtimes with a robust, immutable system architecture to ensure stability and ease of deployment.

## Target Audience

This guide is intended for:
- **Contributors**: Developers looking to improve the core system, add features, or fix bugs.
- **Maintainers**: Individuals responsible for managing the build pipeline and release process.
- **Image Builders**: Users who need to create custom ISO images with specific hardware drivers, pre-loaded models, or modified security policies.

## Technology Stack

NeuralDrive leverages several key technologies to provide a seamless experience:
- **Base System**: Debian 12 (Bookworm) managed via the `live-build` framework.
- **Inference Engine**: Ollama for efficient local LLM execution.
- **User Interface**: Open WebUI for a modern, feature-rich chat interface.
- **Edge Proxy**: Caddy server for TLS termination, routing, and authentication.
- **System Management**: A custom FastAPI-based System API and a Textual-based TUI for console interactions.

The project prioritizes security through systemd hardening, dedicated service users, and an automated TLS certificate management system.

## Project Vision

NeuralDrive aims to bridge the gap between complex AI research environments and production-ready appliances. By treating the entire OS as a single, reproducible unit, we ensure that the environment remains consistent across different hardware configurations.

For end-user documentation covering installation and basic usage, refer to the [User Guide](../../user-guide/src/introduction.md).

