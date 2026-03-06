# Google Home CLI

Control your Google Home/Nest devices from the command line. Broadcast messages, send commands, and more.

## Installation

```bash
pip install google-home-cli
# or from source
pip install -e .
```

## Setup

### 1. Create Google Cloud Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select an existing one
3. Enable the [Google Assistant API](https://console.cloud.google.com/apis/library/embeddedassistant.googleapis.com)
4. Go to **APIs & Services > Credentials**
5. Click **Create Credentials > OAuth client ID**
6. Select **Desktop app** as the application type
7. Download the JSON file

### 2. Initialize and Authenticate

```bash
# Copy your credentials
ghome auth init ~/Downloads/client_secret_XXX.json

# Complete OAuth flow (opens a browser window)
ghome auth login
```

### Authentication Commands

| Command | Description |
|---------|-------------|
| `ghome auth init <path>` | Copy your client secret JSON to the config directory |
| `ghome auth login` | Run the OAuth flow and save credentials |
| `ghome auth status` | Show current authentication status |
| `ghome auth logout` | Clear stored credentials |

### Credential Storage

Credentials are stored in `~/.config/ghome/` with restricted file permissions:

- `client_secret.json` — your Google Cloud OAuth client secret (mode `0600`)
- `credentials.json` — your OAuth token and refresh token (mode `0600`)

The config directory is created with mode `0700` (owner-only access).

### Token Refresh

OAuth tokens expire after a period of time. The CLI automatically refreshes expired tokens using your stored refresh token — no need to re-run `ghome auth login` unless the refresh token itself is revoked.

## Usage

### Broadcast a Message

```bash
ghome broadcast Dinner is ready!
ghome b The package has arrived
```

### Send Any Command

```bash
ghome command set the volume to 5
ghome c what time is it
ghome c turn off the kitchen lights
```

> Quotes are optional — multiple words are joined automatically.

### Shortcuts

Both commands have single-letter aliases:

| Full command | Alias |
|---|---|
| `ghome broadcast` | `ghome b` |
| `ghome command` | `ghome c` |

### Interactive Mode

Both `broadcast` and `command` support interactive mode with command history (up/down arrow navigation):

```bash
ghome broadcast --interactive
> Dinner is ready
Broadcast sent.
> quit

ghome command --interactive
> set the volume to 10
Done.
> what's the weather
The weather is...
> quit
```

## Troubleshooting

**"Not authenticated" error:**
Run `ghome auth login` to complete the OAuth flow.

**"Client secret not found" error:**
Run `ghome auth init <path-to-your-client-secret.json>` first.

**"Token expired" error:**
This usually means your refresh token was revoked. Run `ghome auth login` to re-authenticate.

**Broadcast not reaching devices:**
- Ensure your Google Home devices are on the same Google account
- Check that the Google Assistant API is enabled in your project

## License

MIT
