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
