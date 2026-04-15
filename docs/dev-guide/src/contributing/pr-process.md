*This chapter is for contributors and maintainers.*

# Pull Request Process

This chapter outlines the steps and requirements for submitting a Pull Request (PR) to the NeuralDrive repository.

## Branching Strategy

All development should occur on branches derived from the `main` branch. Use descriptive names for your branches:
- `feat/description-of-feature`
- `fix/description-of-bug`
- `docs/description-of-docs-change`

## Preparation

Before submitting your PR:
1. **Sync with Main**: Rebase your branch on the latest `main` to ensure there are no merge conflicts.
2. **Run Tests**: Ensure all automated tests pass locally.
3. **Linting**: Run `shellcheck` on shell scripts and `ruff` on Python files.
4. **Documentation**: Update any relevant documentation files if your changes affect the system architecture or user experience.

## Submission

When creating the PR on GitHub:
- Provide a clear and concise title using [Conventional Commits](./code-style.md) format.
- Use the PR template to describe the changes, the motivation behind them, and how they were tested.
- Reference any related issues (e.g., `Closes #123`).

## Review and Feedback

- At least one maintainer must review and approve the PR before it can be merged.
- Be prepared to address feedback and make requested changes.
- If you make updates, push them to the same branch; the PR will update automatically.

## CI Requirements

The following checks must pass for a PR to be considered for merging:
- **Build Validation**: The `live-build` configuration must be valid.
- **Linting**: All linters must report zero issues.
- **API Tests**: The `pytest` suite for the System API must pass.

## Merging Policy

NeuralDrive uses a **Squash and Merge** policy. This keeps the main branch history clean and ensures that each feature or fix is represented by a single, well-documented commit.

> **Note**: Only maintainers have the permission to merge PRs into the `main` branch.

