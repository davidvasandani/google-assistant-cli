# tests/test_auth.py
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

import pytest

import google.oauth2.credentials
from ghome.auth import load_credentials, save_credentials, CredentialsNotFoundError, init_client_secret, ClientSecretNotFoundError, run_oauth_flow


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


def test_run_oauth_flow_raises_when_no_client_secret(tmp_path):
    with patch("ghome.auth.get_client_secret_path", return_value=tmp_path / "missing.json"):
        with pytest.raises(ClientSecretNotFoundError):
            run_oauth_flow()


def test_save_credentials_persists_expiry(tmp_path):
    expiry = datetime(2020, 1, 1, tzinfo=timezone.utc)
    creds = google.oauth2.credentials.Credentials(
        token="test_token",
        refresh_token="test_refresh",
        token_uri="https://oauth2.googleapis.com/token",
        client_id="test_client_id",
        client_secret="test_client_secret",
        expiry=expiry,
    )
    creds_path = tmp_path / "credentials.json"

    with patch("ghome.auth.get_config_dir", return_value=tmp_path):
        with patch("ghome.auth.get_credentials_path", return_value=creds_path):
            save_credentials(creds)

    saved = json.loads(creds_path.read_text())
    assert "expiry" in saved
    assert "2020-01-01" in saved["expiry"]


def test_load_credentials_restores_expiry(tmp_path):
    past = datetime(2020, 1, 1, tzinfo=timezone.utc)
    creds_data = {
        "token": "test_token",
        "refresh_token": "test_refresh",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "expiry": past.isoformat(),
    }
    creds_path = tmp_path / "credentials.json"
    creds_path.write_text(json.dumps(creds_data))

    with patch("ghome.auth.get_credentials_path", return_value=creds_path):
        with patch("ghome.auth.get_config_dir", return_value=tmp_path):
            with patch("google.oauth2.credentials.Credentials.refresh"):
                result = load_credentials()

    assert result.expiry is not None


def test_load_credentials_refreshes_expired_token(tmp_path):
    past = datetime(2020, 1, 1, tzinfo=timezone.utc)
    creds_data = {
        "token": "test_token",
        "refresh_token": "test_refresh",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "expiry": past.isoformat(),
    }
    creds_path = tmp_path / "credentials.json"
    creds_path.write_text(json.dumps(creds_data))

    with patch("ghome.auth.get_credentials_path", return_value=creds_path):
        with patch("ghome.auth.get_config_dir", return_value=tmp_path):
            with patch("google.oauth2.credentials.Credentials.refresh") as mock_refresh:
                load_credentials()

    mock_refresh.assert_called_once()
