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
