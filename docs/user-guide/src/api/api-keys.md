*This chapter is for everyone.*

# API Keys

NeuralDrive uses a token-based authentication system to secure access to its APIs. Every request made to the public interface (port 8443) must include a valid API key.

## Key Format

API keys follow a standard prefix-based format:
`nd-xxxxxxxxxxxxxxxxxxxx`

The `nd-` prefix ensures that keys are easily identifiable in configuration files and logs.

## Finding Your Key

There are several ways to retrieve your current API key:

*   **First-Boot:** On your first login to the NeuralDrive console, the initial API key is displayed in the welcome banner.
*   **NeuralDrive TUI:** Launch the Text User Interface by running `neuraldrive-tui` on the server. Navigate to the **Security** or **API** section to view the active key.
*   **System Files:** If you have terminal access, the key is stored in plain text at `/etc/neuraldrive/api.key`.

## Rotating API Keys

For security reasons, we recommend rotating your API key periodically or immediately if you suspect it has been compromised.

### Using the TUI

1.  Open `neuraldrive-tui`.
2.  Select **Security** > **Rotate API Key**.
3.  Confirm the action. The TUI will generate a new key, update the local configuration files, reload the Caddy service, and display the new key.

### Using the System API

You can also rotate the key programmatically via the System Management API.

```bash
curl --cacert neuraldrive-ca.crt \
  -X POST https://neuraldrive.local:8443/system/api-keys/rotate \
  -H "Authorization: Bearer <CURRENT_API_KEY>"
```

The response will contain the newly generated key. Note that the old key becomes invalid immediately after this call.

## Pre-setting Keys in Custom Images

When building custom NeuralDrive images using `neuraldrive-build.yaml`, you can define a static API key in the configuration:

```yaml
security:
  api_key: "nd-mycustomapikey12345"
```

This allows for pre-configured deployments where the API key is known before the first boot. If this field is omitted, NeuralDrive will generate a random key during the initialization process.
