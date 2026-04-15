*This chapter is for contributors and maintainers.*

# How to Contribute

NeuralDrive is a community-driven project. We welcome contributions of all kinds, from core system improvements to documentation updates and bug reports.

## Finding an Issue

If you are looking for a place to start, check the GitHub Issues page for labels like `good first issue` or `help wanted`. These are specifically curated for new contributors.

For more complex features, it is recommended to search the existing issues or start a new Discussion thread to ensure your proposed approach aligns with the project's long-term architecture.

## Types of Contributions

### Core Code
Contributions to the build system (`live-build` configs), service units, or system scripts (`gpu-detect.sh`, `first-boot.sh`). This requires familiarity with Debian and shell scripting.

### Applications
Development of the custom Python applications, including the FastAPI System API and the Textual-based TUI.

### Documentation
Improving this Developer Guide or the User Guide. Clear documentation is as important as working code.

### Testing and QA
Testing the latest snapshots on a variety of hardware (NVIDIA, AMD, Intel GPUs) and reporting the results.

## Communication Channels

- **GitHub Discussions**: The primary place for architectural debate and general questions.
- **Discord/Matrix**: For real-time coordination and quick troubleshooting (links available in the README).

## Contribution Workflow

1. Fork the repository.
2. Create a new branch for your work.
3. Implement your changes and add tests where appropriate.
4. Ensure your code follows the [Code Style Guidelines](./code-style.md).
5. Submit a Pull Request.

> **Note**: All contributors must adhere to the project's Code of Conduct to ensure a welcoming and inclusive environment for everyone.

