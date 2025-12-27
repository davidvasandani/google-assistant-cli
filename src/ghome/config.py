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
