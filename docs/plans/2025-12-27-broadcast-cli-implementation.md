# Google Home CLI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI that broadcasts messages to Google Home devices via the Google Assistant SDK.

**Architecture:** Click CLI wrapping gassist-text TextAssistant. OAuth credentials stored in ~/.config/ghome/. Commands: `ghome auth init/login/status/logout` and `ghome broadcast`.

**Tech Stack:** Python 3.10+, click, gassist-text, google-auth-oauthlib, pytest

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `src/ghome/__init__.py`
- Create: `.gitignore`

**Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "google-home-cli"
version = "0.1.0"
description = "CLI to broadcast messages to Google Home devices"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "click>=8.0",
    "gassist-text>=0.0.10",
    "google-auth-oauthlib>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-mock>=3.0",
]

[project.scripts]
ghome = "ghome.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
```

**Step 2: Create package init**

```python
# src/ghome/__init__.py
"""Google Home CLI - Broadcast messages to Google Home devices."""

__version__ = "0.1.0"
```

**Step 3: Create .gitignore**

```
__pycache__/
*.py[cod]
.eggs/
*.egg-info/
dist/
build/
.venv/
venv/
.env
*.egg
.pytest_cache/
```

**Step 4: Create virtual environment and install**

Run: `python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`

**Step 5: Verify installation**

Run: `ghome --help`
Expected: Error (cli.py doesn't exist yet) - that's fine for now

**Step 6: Commit**

```bash
git add pyproject.toml src/ghome/__init__.py .gitignore
git commit -m "feat: initialize project with pyproject.toml"
```

---

## Task 2: Config Module

**Files:**
- Create: `src/ghome/config.py`
- Create: `tests/test_config.py`

**Step 1: Write the failing test**

```python
# tests/test_config.py
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from ghome.config import get_config_dir, get_client_secret_path, get_credentials_path


def test_get_config_dir_returns_path():
    with patch.dict(os.environ, {"HOME": "/home/testuser"}):
        result = get_config_dir()
        assert result == Path("/home/testuser/.config/ghome")


def test_get_client_secret_path():
    with patch.dict(os.environ, {"HOME": "/home/testuser"}):
        result = get_client_secret_path()
        assert result == Path("/home/testuser/.config/ghome/client_secret.json")


def test_get_credentials_path():
    with patch.dict(os.environ, {"HOME": "/home/testuser"}):
        result = get_credentials_path()
        assert result == Path("/home/testuser/.config/ghome/credentials.json")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'ghome.config'"

**Step 3: Write minimal implementation**

```python
# src/ghome/config.py
"""Configuration and path management."""

from pathlib import Path


def get_config_dir() -> Path:
    """Return the config directory path."""
    return Path.home() / ".config" / "ghome"


def get_client_secret_path() -> Path:
    """Return the path to client_secret.json."""
    return get_config_dir() / "client_secret.json"


def get_credentials_path() -> Path:
    """Return the path to credentials.json."""
    return get_config_dir() / "credentials.json"
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/ghome/config.py tests/test_config.py
git commit -m "feat: add config module for path management"
```

---

## Task 3: Auth Module - Credential Loading

**Files:**
- Create: `src/ghome/auth.py`
- Create: `tests/test_auth.py`

**Step 1: Write the failing test for loading credentials**

```python
# tests/test_auth.py
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from ghome.auth import load_credentials, CredentialsNotFoundError


def test_load_credentials_raises_when_file_missing(tmp_path):
    with patch("ghome.auth.get_credentials_path", return_value=tmp_path / "missing.json"):
        with pytest.raises(CredentialsNotFoundError):
            load_credentials()


def test_load_credentials_returns_credentials_object(tmp_path):
    creds_path = tmp_path / "credentials.json"
    creds_data = {
        "token": "test_token",
        "refresh_token": "test_refresh",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
    }
    creds_path.write_text(json.dumps(creds_data))

    with patch("ghome.auth.get_credentials_path", return_value=creds_path):
        result = load_credentials()
        assert result is not None
        assert result.token == "test_token"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_auth.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

```python
# src/ghome/auth.py
"""OAuth credential management."""

import json

import google.oauth2.credentials

from ghome.config import get_credentials_path


class CredentialsNotFoundError(Exception):
    """Raised when credentials file is not found."""
    pass


def load_credentials() -> google.oauth2.credentials.Credentials:
    """Load OAuth credentials from the credentials file."""
    creds_path = get_credentials_path()

    if not creds_path.exists():
        raise CredentialsNotFoundError(
            f"Credentials not found. Run 'ghome auth login' first."
        )

    with open(creds_path, "r") as f:
        creds_data = json.load(f)

    return google.oauth2.credentials.Credentials(
        token=creds_data.get("token"),
        refresh_token=creds_data.get("refresh_token"),
        token_uri=creds_data.get("token_uri"),
        client_id=creds_data.get("client_id"),
        client_secret=creds_data.get("client_secret"),
    )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_auth.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/ghome/auth.py tests/test_auth.py
git commit -m "feat: add credential loading to auth module"
```

---

## Task 4: Auth Module - OAuth Flow

**Files:**
- Modify: `src/ghome/auth.py`
- Modify: `tests/test_auth.py`

**Step 1: Write the failing test for init command**

```python
# Add to tests/test_auth.py
import shutil

from ghome.auth import init_client_secret, ClientSecretNotFoundError


def test_init_client_secret_copies_file(tmp_path):
    source = tmp_path / "source" / "client_secret.json"
    source.parent.mkdir()
    source.write_text('{"installed": {"client_id": "test"}}')

    dest_dir = tmp_path / "config"
    dest_file = dest_dir / "client_secret.json"

    with patch("ghome.auth.get_config_dir", return_value=dest_dir):
        with patch("ghome.auth.get_client_secret_path", return_value=dest_file):
            init_client_secret(source)
            assert dest_file.exists()
            assert json.loads(dest_file.read_text()) == {"installed": {"client_id": "test"}}


def test_init_client_secret_raises_when_source_missing(tmp_path):
    with pytest.raises(ClientSecretNotFoundError):
        init_client_secret(tmp_path / "nonexistent.json")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_auth.py::test_init_client_secret_copies_file -v`
Expected: FAIL

**Step 3: Add init_client_secret implementation**

```python
# Add to src/ghome/auth.py
from pathlib import Path
import shutil

from ghome.config import get_config_dir, get_client_secret_path


class ClientSecretNotFoundError(Exception):
    """Raised when client secret file is not found."""
    pass


def init_client_secret(source_path: Path) -> None:
    """Copy client secret file to config directory."""
    if not source_path.exists():
        raise ClientSecretNotFoundError(f"File not found: {source_path}")

    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    dest_path = get_client_secret_path()
    shutil.copy(source_path, dest_path)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_auth.py -v`
Expected: PASS

**Step 5: Write test for run_oauth_flow**

```python
# Add to tests/test_auth.py
from ghome.auth import run_oauth_flow


def test_run_oauth_flow_raises_when_no_client_secret(tmp_path):
    with patch("ghome.auth.get_client_secret_path", return_value=tmp_path / "missing.json"):
        with pytest.raises(ClientSecretNotFoundError):
            run_oauth_flow()
```

**Step 6: Run test to verify it fails**

Run: `pytest tests/test_auth.py::test_run_oauth_flow_raises_when_no_client_secret -v`
Expected: FAIL

**Step 7: Add run_oauth_flow implementation**

```python
# Add to src/ghome/auth.py
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/assistant-sdk-prototype"]


def run_oauth_flow() -> google.oauth2.credentials.Credentials:
    """Run OAuth flow and save credentials."""
    client_secret_path = get_client_secret_path()

    if not client_secret_path.exists():
        raise ClientSecretNotFoundError(
            "Client secret not found. Run 'ghome auth init <path>' first."
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_secret_path),
        scopes=SCOPES,
    )

    credentials = flow.run_local_server(port=0)
    save_credentials(credentials)
    return credentials


def save_credentials(credentials: google.oauth2.credentials.Credentials) -> None:
    """Save credentials to file."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    creds_path = get_credentials_path()
    creds_data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
    }

    with open(creds_path, "w") as f:
        json.dump(creds_data, f)
```

**Step 8: Run tests**

Run: `pytest tests/test_auth.py -v`
Expected: PASS

**Step 9: Commit**

```bash
git add src/ghome/auth.py tests/test_auth.py
git commit -m "feat: add OAuth flow to auth module"
```

---

## Task 5: Assistant Module

**Files:**
- Create: `src/ghome/assistant.py`
- Create: `tests/test_assistant.py`

**Step 1: Write the failing test**

```python
# tests/test_assistant.py
from unittest.mock import patch, MagicMock

import pytest

from ghome.assistant import broadcast_message, BroadcastError


def test_broadcast_message_sends_correct_command():
    mock_assistant = MagicMock()
    mock_assistant.assist.return_value = ("Broadcast sent", None)

    with patch("ghome.assistant.TextAssistant") as MockTextAssistant:
        MockTextAssistant.return_value.__enter__.return_value = mock_assistant

        mock_creds = MagicMock()
        result = broadcast_message("Dinner is ready", mock_creds)

        mock_assistant.assist.assert_called_once_with("broadcast Dinner is ready")
        assert result == "Broadcast sent"


def test_broadcast_message_raises_on_empty_message():
    mock_creds = MagicMock()

    with pytest.raises(BroadcastError, match="Message cannot be empty"):
        broadcast_message("", mock_creds)


def test_broadcast_message_raises_on_too_long_message():
    mock_creds = MagicMock()
    long_message = "a" * 201

    with pytest.raises(BroadcastError, match="exceeds maximum length"):
        broadcast_message(long_message, mock_creds)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_assistant.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/ghome/assistant.py
"""Google Assistant interaction."""

import google.oauth2.credentials
from gassist_text import TextAssistant


class BroadcastError(Exception):
    """Raised when broadcast fails."""
    pass


MAX_MESSAGE_LENGTH = 200


def broadcast_message(
    message: str,
    credentials: google.oauth2.credentials.Credentials,
) -> str:
    """Broadcast a message to all Google Home devices."""
    message = message.strip()

    if not message:
        raise BroadcastError("Message cannot be empty")

    if len(message) > MAX_MESSAGE_LENGTH:
        raise BroadcastError(
            f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters"
        )

    command = f"broadcast {message}"

    with TextAssistant(credentials) as assistant:
        response_text, _ = assistant.assist(command)

    return response_text or "Broadcast sent"
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_assistant.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/ghome/assistant.py tests/test_assistant.py
git commit -m "feat: add assistant module for broadcasting"
```

---

## Task 6: CLI - Main Entry Point

**Files:**
- Create: `src/ghome/cli.py`
- Create: `tests/test_cli.py`

**Step 1: Write the failing test**

```python
# tests/test_cli.py
from click.testing import CliRunner

from ghome.cli import main


def test_main_shows_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Google Home CLI" in result.output


def test_main_shows_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/ghome/cli.py
"""Command-line interface for Google Home CLI."""

import click

from ghome import __version__


@click.group()
@click.version_option(version=__version__)
def main():
    """Google Home CLI - Broadcast messages to Google Home devices."""
    pass
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/ghome/cli.py tests/test_cli.py
git commit -m "feat: add CLI main entry point"
```

---

## Task 7: CLI - Auth Commands

**Files:**
- Modify: `src/ghome/cli.py`
- Modify: `tests/test_cli.py`

**Step 1: Write failing tests for auth commands**

```python
# Add to tests/test_cli.py
from unittest.mock import patch, MagicMock
from pathlib import Path


def test_auth_init_copies_client_secret(tmp_path):
    source = tmp_path / "client_secret.json"
    source.write_text('{"installed": {}}')

    runner = CliRunner()
    with patch("ghome.cli.init_client_secret") as mock_init:
        result = runner.invoke(main, ["auth", "init", str(source)])
        assert result.exit_code == 0
        mock_init.assert_called_once()


def test_auth_init_fails_with_missing_file():
    runner = CliRunner()
    result = runner.invoke(main, ["auth", "init", "/nonexistent/file.json"])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_auth_login_runs_oauth_flow():
    runner = CliRunner()
    with patch("ghome.cli.run_oauth_flow") as mock_flow:
        with patch("ghome.cli.get_client_secret_path") as mock_path:
            mock_path.return_value = Path("/fake/client_secret.json")
            mock_path.return_value.exists = MagicMock(return_value=True)
            result = runner.invoke(main, ["auth", "login"])
            # Will fail without real OAuth, but tests the flow
            mock_flow.assert_called_once()


def test_auth_status_shows_not_configured(tmp_path):
    runner = CliRunner()
    with patch("ghome.cli.get_client_secret_path", return_value=tmp_path / "missing.json"):
        with patch("ghome.cli.get_credentials_path", return_value=tmp_path / "missing2.json"):
            result = runner.invoke(main, ["auth", "status"])
            assert "not configured" in result.output.lower() or "not found" in result.output.lower()


def test_auth_logout_clears_credentials(tmp_path):
    creds_file = tmp_path / "credentials.json"
    creds_file.write_text("{}")

    runner = CliRunner()
    with patch("ghome.cli.get_credentials_path", return_value=creds_file):
        result = runner.invoke(main, ["auth", "logout"])
        assert result.exit_code == 0
        assert not creds_file.exists()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_auth_init_copies_client_secret -v`
Expected: FAIL

**Step 3: Add auth commands implementation**

```python
# Replace src/ghome/cli.py with:
"""Command-line interface for Google Home CLI."""

import sys
from pathlib import Path

import click

from ghome import __version__
from ghome.auth import (
    init_client_secret,
    run_oauth_flow,
    load_credentials,
    ClientSecretNotFoundError,
    CredentialsNotFoundError,
)
from ghome.config import get_client_secret_path, get_credentials_path


@click.group()
@click.version_option(version=__version__)
def main():
    """Google Home CLI - Broadcast messages to Google Home devices."""
    pass


@main.group()
def auth():
    """Manage authentication."""
    pass


@auth.command("init")
@click.argument("client_secret_path", type=click.Path(exists=True, path_type=Path))
def auth_init(client_secret_path: Path):
    """Initialize with client secret file from Google Cloud Console."""
    try:
        init_client_secret(client_secret_path)
        click.echo(f"Client secret copied to {get_client_secret_path()}")
    except ClientSecretNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@auth.command("login")
def auth_login():
    """Complete OAuth flow to authorize access."""
    try:
        run_oauth_flow()
        click.echo("Authentication successful!")
    except ClientSecretNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("Run 'ghome auth init <path>' first.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error during authentication: {e}", err=True)
        sys.exit(1)


@auth.command("status")
def auth_status():
    """Show current authentication status."""
    client_secret = get_client_secret_path()
    credentials = get_credentials_path()

    if not client_secret.exists():
        click.echo("Status: Not configured")
        click.echo("Run 'ghome auth init <path>' to set up.")
        return

    if not credentials.exists():
        click.echo("Status: Client secret configured, but not logged in")
        click.echo("Run 'ghome auth login' to authenticate.")
        return

    click.echo("Status: Authenticated")
    click.echo(f"Credentials: {credentials}")


@auth.command("logout")
def auth_logout():
    """Clear stored credentials."""
    creds_path = get_credentials_path()

    if creds_path.exists():
        creds_path.unlink()
        click.echo("Credentials cleared.")
    else:
        click.echo("No credentials to clear.")
```

**Step 4: Run tests**

Run: `pytest tests/test_cli.py -v`
Expected: Most tests PASS (some may need adjustment)

**Step 5: Commit**

```bash
git add src/ghome/cli.py tests/test_cli.py
git commit -m "feat: add auth commands to CLI"
```

---

## Task 8: CLI - Broadcast Command

**Files:**
- Modify: `src/ghome/cli.py`
- Modify: `tests/test_cli.py`

**Step 1: Write failing tests for broadcast**

```python
# Add to tests/test_cli.py
def test_broadcast_sends_message():
    runner = CliRunner()
    with patch("ghome.cli.load_credentials") as mock_load:
        with patch("ghome.cli.broadcast_message") as mock_broadcast:
            mock_broadcast.return_value = "Broadcast sent"
            result = runner.invoke(main, ["broadcast", "Dinner is ready"])
            assert result.exit_code == 0
            mock_broadcast.assert_called_once()
            assert "Broadcast sent" in result.output


def test_broadcast_fails_without_auth():
    runner = CliRunner()
    with patch("ghome.cli.load_credentials") as mock_load:
        mock_load.side_effect = CredentialsNotFoundError("No creds")
        result = runner.invoke(main, ["broadcast", "test"])
        assert result.exit_code == 1
        assert "ghome auth login" in result.output.lower()


def test_broadcast_interactive_mode():
    runner = CliRunner()
    with patch("ghome.cli.load_credentials"):
        with patch("ghome.cli.broadcast_message") as mock_broadcast:
            mock_broadcast.return_value = "Broadcast sent"
            result = runner.invoke(
                main,
                ["broadcast", "--interactive"],
                input="Hello\nWorld\nquit\n"
            )
            assert mock_broadcast.call_count == 2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_broadcast_sends_message -v`
Expected: FAIL

**Step 3: Add broadcast command implementation**

```python
# Add to src/ghome/cli.py, after auth commands:

from ghome.assistant import broadcast_message, BroadcastError


@main.command()
@click.argument("message", required=False)
@click.option("-i", "--interactive", is_flag=True, help="Interactive shell mode")
@click.option("-v", "--verbose", is_flag=True, help="Show debug output")
def broadcast(message: str | None, interactive: bool, verbose: bool):
    """Broadcast a message to all Google Home devices."""
    try:
        credentials = load_credentials()
    except CredentialsNotFoundError:
        click.echo("Error: Not authenticated.", err=True)
        click.echo("Run 'ghome auth login' first.", err=True)
        sys.exit(1)

    if interactive:
        _run_interactive_mode(credentials, verbose)
    elif message:
        _send_single_broadcast(message, credentials, verbose)
    else:
        click.echo("Error: Message required. Use --interactive for shell mode.", err=True)
        sys.exit(2)


def _send_single_broadcast(message: str, credentials, verbose: bool):
    """Send a single broadcast message."""
    try:
        response = broadcast_message(message, credentials)
        click.echo(response)
    except BroadcastError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)
    except Exception as e:
        if verbose:
            click.echo(f"Error: {e}", err=True)
        else:
            click.echo("Error: Failed to send broadcast. Use --verbose for details.", err=True)
        sys.exit(2)


def _run_interactive_mode(credentials, verbose: bool):
    """Run interactive broadcast shell."""
    click.echo("Interactive mode. Type 'quit' to exit.")

    while True:
        try:
            message = click.prompt(">", prompt_suffix=" ")
        except (EOFError, KeyboardInterrupt):
            click.echo("\nExiting.")
            break

        if message.lower() in ("quit", "exit", "q"):
            break

        if not message.strip():
            continue

        try:
            response = broadcast_message(message, credentials)
            click.echo(response)
        except BroadcastError as e:
            click.echo(f"Error: {e}", err=True)
        except Exception as e:
            if verbose:
                click.echo(f"Error: {e}", err=True)
            else:
                click.echo("Error: Failed to send. Use --verbose for details.", err=True)
```

**Step 4: Run tests**

Run: `pytest tests/test_cli.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/ghome/cli.py tests/test_cli.py
git commit -m "feat: add broadcast command to CLI"
```

---

## Task 9: README and Final Polish

**Files:**
- Create: `README.md`

**Step 1: Create README**

```markdown
# Google Home CLI

Broadcast messages to your Google Home/Nest speakers from the command line.

## Installation

```bash
pip install google-home-cli
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

# Complete OAuth flow
ghome auth login
```

## Usage

### Single Broadcast

```bash
ghome broadcast "Dinner is ready!"
ghome broadcast "The package has arrived"
```

### Interactive Mode

```bash
ghome broadcast --interactive
> Dinner is ready
Broadcast sent.
> Kids come downstairs
Broadcast sent.
> quit
```

### Check Auth Status

```bash
ghome auth status
```

## Troubleshooting

**"Not authenticated" error:**
Run `ghome auth login` to complete the OAuth flow.

**"Client secret not found" error:**
Run `ghome auth init <path-to-your-client-secret.json>` first.

**Broadcast not reaching devices:**
- Ensure your Google Home devices are on the same Google account
- Check that the Google Assistant API is enabled in your project

## License

MIT
```

**Step 2: Run full test suite**

Run: `pytest -v`
Expected: All tests PASS

**Step 3: Verify CLI works**

Run: `ghome --help`
Run: `ghome auth --help`
Run: `ghome broadcast --help`

**Step 4: Final commit**

```bash
git add README.md
git commit -m "docs: add README with setup instructions"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Project setup | pyproject.toml, __init__.py, .gitignore |
| 2 | Config module | config.py |
| 3 | Auth - credential loading | auth.py |
| 4 | Auth - OAuth flow | auth.py |
| 5 | Assistant module | assistant.py |
| 6 | CLI - main entry | cli.py |
| 7 | CLI - auth commands | cli.py |
| 8 | CLI - broadcast command | cli.py |
| 9 | README and polish | README.md |

Total: 9 tasks with TDD approach throughout.
