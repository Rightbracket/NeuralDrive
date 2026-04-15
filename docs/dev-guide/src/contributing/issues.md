*This chapter is for contributors and maintainers.*

# Issue Guidelines

We use GitHub Issues to track bugs, feature requests, and tasks. Effective issue reporting helps maintainers understand and resolve problems faster.

## Bug Reports

Before filing a bug report, search the existing issues to see if it has already been reported. If not, use the "Bug Report" template and include:
- **System Version**: The version of NeuralDrive you are using (found in `/etc/neuraldrive/version`).
- **Hardware Specs**: CPU, RAM, and specifically your GPU model and driver version.
- **Steps to Reproduce**: A clear, numbered list of steps that lead to the issue.
- **Expected vs Actual Behavior**: What you expected to happen and what actually happened.
- **Logs**: Relevant logs from `journalctl` or the System API.

## Feature Requests

Feature requests should be submitted using the "Feature Request" template. Good requests include:
- **Problem Statement**: What problem does this feature solve?
- **Proposed Solution**: A description of how the feature should work.
- **Alternatives Considered**: Any other ways you thought about solving the problem.
- **Context**: Why this feature is important for the NeuralDrive appliance.

## Issue Labels

Maintainers use several labels to organize the backlog:
- `bug`: Something is broken.
- `enhancement`: New feature or improvement.
- `documentation`: Changes to docs.
- `help wanted`: Tasks that are ready for community contribution.
- `good first issue`: Simple tasks for new contributors.
- `triage`: New issues that need further investigation.

## Issue Lifecycle

1. **New**: The issue has been created and is waiting for triage.
2. **Accepted**: A maintainer has verified the bug or approved the feature request.
3. **In Progress**: Someone is actively working on the issue.
4. **Resolved**: The fix or feature has been merged into `main`.

> **Tip**: If you find an issue you want to work on, please leave a comment so others know it is being handled.

