# Google Home CLI - Broadcast Feature Design

## Overview

A Python CLI tool to broadcast voice messages to Google Home/Nest speakers using the Google Assistant SDK.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    google-home-cli                       │
├─────────────────────────────────────────────────────────┤
│  CLI Layer (click)                                      │
│  ├── ghome broadcast "message"     (one-shot mode)     │
│  └── ghome broadcast --interactive (shell mode)        │
├─────────────────────────────────────────────────────────┤
│  Assistant Client                                        │
│  └── Handles OAuth2, sends text queries to Assistant    │
├─────────────────────────────────────────────────────────┤
│  Google Assistant SDK (gRPC)                            │
│  └── google-assistant-sdk + google-auth-oauthlib        │
└─────────────────────────────────────────────────────────┘
            │
            ▼
    Google Assistant API
            │
            ▼
    Your Google Home Devices
```

### How It Works

1. CLI accepts your text message
2. Converts it to a Google Assistant command: `"broadcast {message}"`
3. Sends via Assistant SDK using your OAuth credentials
4. Assistant broadcasts to all linked Home/Nest speakers

### Key Files

- `ghome/cli.py` - Click-based CLI entry point
- `ghome/assistant.py` - Assistant SDK wrapper
- `ghome/auth.py` - OAuth credential management
- `credentials/` - Stores OAuth tokens (gitignored)

## Authentication & Setup

### First-Time Setup

```bash
ghome auth login
```

This command will:
1. Open browser to Google OAuth consent screen
2. User grants "Google Assistant" permissions
3. Save refresh token to `~/.config/ghome/credentials.json`

### Prerequisites

1. Enable "Google Assistant API" in your existing GCP project
2. Create OAuth 2.0 credentials (Desktop app type)
3. Download `client_secret.json` to `~/.config/ghome/`
4. Run `ghome auth login`

### Credential Storage

```
~/.config/ghome/
├── client_secret.json    (user downloads from GCP Console)
└── credentials.json      (generated after OAuth flow)
```

### Token Refresh

- Handled automatically by `google-auth-oauthlib`
- Refresh token is long-lived; re-auth rarely needed
- If token expires/revokes: `ghome auth login` again

### Device Registration

- Google Assistant SDK requires a device model ID
- Register a default model during first auth
- Stored in `~/.config/ghome/device_config.json`

## CLI Interface

### Installation

```bash
pip install google-home-cli
# or from source
pip install -e .
```

### Commands

```bash
# One-shot broadcast (default)
ghome broadcast "Dinner is ready"
ghome broadcast "The package has arrived"

# Interactive mode
ghome broadcast --interactive
> Dinner is ready
Broadcasting...
> Kids come downstairs
Broadcasting...
> quit

# Auth management
ghome auth login      # Initial OAuth flow
ghome auth status     # Show current auth state
ghome auth logout     # Clear stored credentials
```

### Exit Codes

- `0` - Success
- `1` - Auth error (credentials missing/expired)
- `2` - API error (network, quota, etc.)

### Options

```
ghome broadcast [OPTIONS] [MESSAGE]

Options:
  -i, --interactive    Enter interactive shell mode
  -v, --verbose        Show debug output
  --help               Show this message and exit
```

### Dependencies

```
click>=8.0
google-assistant-sdk>=0.6.0
google-auth-oauthlib>=1.0
grpcio>=1.50
```

## Error Handling

| Scenario | User Message | Exit Code |
|----------|--------------|-----------|
| No credentials found | `Run 'ghome auth login' first` | 1 |
| Token expired | `Session expired. Run 'ghome auth login'` | 1 |
| No internet | `Network error: Unable to reach Google` | 2 |
| API quota exceeded | `Rate limited. Wait a moment and retry` | 2 |
| Empty message | `Message cannot be empty` | 2 |

### Validation

- Message must be non-empty string
- Max message length: 200 characters (Google's limit for broadcasts)
- Strip leading/trailing whitespace

### Graceful Degradation

- If broadcast fails, show clear error with actionable next step
- In interactive mode, errors don't exit - just show error and prompt again

### Logging

- Default: errors only
- `--verbose`: includes API request/response details for debugging
