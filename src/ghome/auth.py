"""OAuth credential management."""

import json
import os
import shutil
from pathlib import Path

import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from ghome.config import get_config_dir, get_client_secret_path, get_credentials_path

SCOPES = ["https://www.googleapis.com/auth/assistant-sdk-prototype"]


class CredentialsNotFoundError(Exception):
    """Raised when credentials file is not found."""
    pass


class ClientSecretNotFoundError(Exception):
    """Raised when client secret file is not found."""
    pass


def load_credentials() -> google.oauth2.credentials.Credentials:
    """Load OAuth credentials from the credentials file."""
    creds_path = get_credentials_path()

    if not creds_path.exists():
        raise CredentialsNotFoundError(
            f"Credentials not found. Run 'ghome auth login' first."
        )

    try:
        with open(creds_path, "r") as f:
            creds_data = json.load(f)
    except json.JSONDecodeError as e:
        raise CredentialsNotFoundError(
            f"Credentials file is invalid JSON. Run 'ghome auth login' to re-authenticate."
        )

    return google.oauth2.credentials.Credentials(
        token=creds_data.get("token"),
        refresh_token=creds_data.get("refresh_token"),
        token_uri=creds_data.get("token_uri"),
        client_id=creds_data.get("client_id"),
        client_secret=creds_data.get("client_secret"),
    )


def init_client_secret(source_path: Path) -> None:
    """Copy client secret file to config directory."""
    if not source_path.exists():
        raise ClientSecretNotFoundError(f"File not found: {source_path}")

    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    dest_path = get_client_secret_path()
    shutil.copy(source_path, dest_path)
    os.chmod(dest_path, 0o600)  # Owner read/write only


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
    config_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

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

    os.chmod(creds_path, 0o600)  # Owner read/write only
