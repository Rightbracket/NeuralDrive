*This chapter is for contributors and maintainers.*

# API Tests

NeuralDrive uses the `pytest` framework to test the System API and ensure that the backend logic remains correct through code changes.

## Test Environment

API tests are located in `tests/test_api.py`. They use the `FastAPI.testclient` to simulate HTTP requests without needing a running server.

### Mocking System Calls
Since many API endpoints interact with the underlying OS (e.g., restarting services, reading logs), the tests use the `unittest.mock` library to simulate these interactions. This allows the tests to run in a non-Debian environment (like a macOS development machine or a standard CI runner).

## Running the Tests

To run the API test suite locally:
```bash
# Ensure your dev venv is active
pip install pytest httpx
pytest tests/test_api.py
```

## Coverage Areas

The test suite covers:

### 1. Authentication
- Verifying that requests without a Bearer token are rejected.
- Verifying that incorrect tokens are rejected.
- Verifying that valid tokens allow access.

### 2. Service Management
- Mocking `systemctl` calls to verify that the API correctly handles service start/stop/restart commands.
- Verifying that the API correctly parses service status output.

### 3. Log Retrieval
- Testing the logic that reads and truncates system journals.
- Ensuring that the API correctly handles cases where a service does not exist or has no logs.

### 4. Configuration Changes
- Verifying that network configuration changes are correctly written to the internal config files.
- Testing the API key rotation logic.

## Adding New Tests

When adding a new endpoint to the System API:
1. Create a corresponding test function in `test_api.py`.
2. Mock any new system calls or filesystem interactions.
3. Assert that the response status code and body match the expected output.

> **Tip**: Use `pytest -v` for verbose output and `pytest --cov` to check the test coverage of the API source code.

