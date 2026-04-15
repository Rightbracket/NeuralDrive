*This chapter is for contributors and maintainers.*

# Code Style and Standards

To maintain a consistent and maintainable codebase, all contributions must adhere to the following style guidelines.

## Shell Scripting

NeuralDrive relies heavily on shell scripts for system configuration and build hooks.

- **Interpreter**: Use `#!/bin/bash` or `#!/bin/sh` as appropriate.
- **Safety**: Start all scripts with `set -euo pipefail`.
- **Indentation**: Use 4 spaces for indentation.
- **Linting**: All scripts must pass `shellcheck` without warnings.
- **Functions**: Define logic in functions rather than a flat script structure.

## Python

The System API and TUI are written in Python.

- **Style**: Adhere to PEP 8.
- **Indentation**: Use 4 spaces.
- **Formatting**: Use `ruff` for both linting and formatting.
- **Types**: Use Python type hints for all function signatures and complex variables.
- **Dependencies**: New dependencies must be added to the appropriate `requirements.txt` file and justified in the PR.

## Configuration Files (YAML/JSON)

- **YAML**: Use 2-space indentation.
- **JSON**: Use 4-space indentation and ensure it is valid via `jq`.

## Commit Messages

We follow the Conventional Commits specification. This allows for automated changelog generation and versioning.

Format: `<type>(<scope>): <description>`

Common types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Changes that do not affect the meaning of the code (formatting, etc.)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

## Documentation

- Use Markdown for all documentation.
- Avoid AI slop phrases and maintain a professional, technical tone.
- Ensure all relative links between chapters are correct.
- Code blocks must have the appropriate language tag (e.g., `bash`, `python`, `yaml`).

