# Google Home CLI - Broadcast Feature Design

## Overview

A Python CLI tool to broadcast voice messages to Google Home/Nest speakers using the Google Assistant SDK, following the same approach as [Home Assistant's Google Assistant SDK integration](https://www.home-assistant.io/integrations/google_assistant_sdk).

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    google-home-cli                       │
├─────────────────────────────────────────────────────────┤
│  CLI Layer (click)                                      │
│  ├── ghome broadcast "message"     (one-shot mode)     │
│  └── ghome broadcast --interactive (shell mode)        │
├─────────────────────────────────────────────────────────┤
│  Assistant Client (ghome/assistant.py)                  │
│  └── Wraps gassist-text TextAssistant                  │
├─────────────────────────────────────────────────────────┤
│  gassist-text + google-assistant-grpc                   │
│  └── Sends text queries via gRPC to Google Assistant   │
└─────────────────────────────────────────────────────────┘
            │
            ▼
    Google Assistant API (gRPC)
            │
            ▼
    Your Google Home/Nest Devices
```

### How It Works

1. CLI accepts your text message
2. Prepends "broadcast " to create command: `"broadcast {message}"`
3. Sends via `gassist-text` TextAssistant using OAuth credentials
4. Google Assistant broadcasts to all linked Home/Nest speakers

### Key Files

- `src/ghome/cli.py` - Click-based CLI entry point
- `src/ghome/assistant.py` - TextAssistant wrapper
- `src/ghome/auth.py` - OAuth credential management
- `src/ghome/config.py` - Configuration and paths

## Authentication & Setup

### Prerequisites

1. Create a Google Cloud project (or use existing)
2. Enable "Google Assistant API" in the project
3. Configure OAuth consent screen (can be "Testing" status)
4. Create OAuth 2.0 credentials (**Desktop app** type - required)
5. Download credentials JSON

### First-Time Setup

```bash
# 1. Place your downloaded credentials
ghome auth init ~/Downloads/client_secret_XXX.json

# 2. Complete OAuth flow
ghome auth login
# Opens browser -> Grant permissions -> Paste auth code
```

### Credential Storage

```
~/.config/ghome/
├── client_secret.json    (copied from user's download)
└── credentials.json      (generated after OAuth flow)
```

### Token Refresh

- Handled automatically by `google-auth-oauthlib`
- Refresh token is long-lived; re-auth rarely needed
- If token expires/revokes: `ghome auth login` again

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
Broadcast sent.
> Kids come downstairs
Broadcast sent.
> quit

# Auth management
ghome auth init <path-to-client-secret>   # Copy credentials
ghome auth login                           # Complete OAuth flow
ghome auth status                          # Show current auth state
ghome auth logout                          # Clear stored credentials
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
gassist-text>=0.0.10
google-auth-oauthlib>=1.0
```

## Error Handling

| Scenario | User Message | Exit Code |
|----------|--------------|-----------|
| No client_secret.json | `Run 'ghome auth init <path>' first` | 1 |
| No credentials.json | `Run 'ghome auth login' first` | 1 |
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

## References

- [Home Assistant Google Assistant SDK](https://www.home-assistant.io/integrations/google_assistant_sdk)
- [gassist-text](https://github.com/tronikos/gassist_text) - Python library for Google Assistant text API
- [google-assistant-grpc](https://pypi.org/project/google-assistant-grpc/) - gRPC bindings
