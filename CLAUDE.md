# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_assistant.py

# Run a specific test
pytest tests/test_assistant.py::test_broadcast_message_sends_correct_command

# Run the CLI (after install)
ghome --help
```

## Architecture

The package (`src/ghome/`) has four modules with a clear dependency flow:

```
cli.py → assistant.py → gassist_text.TextAssistant (external)
       → auth.py      → google-auth-oauthlib (external)
       → config.py
```

**`config.py`** — Pure path resolution. All config lives in `~/.config/ghome/`. No dependencies on other modules.

**`auth.py`** — OAuth credential lifecycle: `init_client_secret` copies the Google Cloud Console JSON file, `run_oauth_flow` opens a browser for OAuth, `load_credentials` reads and auto-refreshes tokens using the refresh token.

**`assistant.py`** — Thin wrapper around `gassist_text.TextAssistant`. Used as a context manager (`with TextAssistant(credentials) as assistant`). `assist()` returns a 3-tuple `(text, html, audio)` — only the first value is used. `broadcast_message` prepends `"broadcast "` to the text; `send_command` passes text through directly.

**`cli.py`** — Click command group (`main`) with two subgroups:
- `auth` group: `init`, `login`, `status`, `logout`
- Top-level commands: `broadcast`, `command`

Both `broadcast` and `command` support a single-argument mode and `--interactive` shell mode. The `--verbose` flag exposes exception details that are otherwise suppressed.

## Key Constraints

- `broadcast_message` enforces a 200-character limit; `send_command` has no length limit.
- The OAuth scope is `https://www.googleapis.com/auth/assistant-sdk-prototype`.
- Credentials and client secret files are stored with `0600` permissions; the config dir uses `0700`.
- Tests mock `ghome.assistant.TextAssistant` using `patch` + a `MagicMock` configured as a context manager. The `assist()` mock must return a 3-tuple.
