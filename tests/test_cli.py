# tests/test_cli.py
from unittest.mock import patch, MagicMock
from pathlib import Path

from click.testing import CliRunner

from ghome.cli import main
from ghome.auth import CredentialsNotFoundError


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
    assert result.exit_code != 0


def test_auth_login_runs_oauth_flow():
    runner = CliRunner()
    with patch("ghome.cli.run_oauth_flow") as mock_flow:
        with patch("ghome.cli.get_client_secret_path") as mock_path:
            mock_path.return_value = MagicMock()
            mock_path.return_value.exists.return_value = True
            result = runner.invoke(main, ["auth", "login"])
            mock_flow.assert_called_once()


def test_auth_status_shows_not_configured(tmp_path):
    runner = CliRunner()
    with patch("ghome.cli.get_client_secret_path", return_value=tmp_path / "missing.json"):
        with patch("ghome.cli.get_credentials_path", return_value=tmp_path / "missing2.json"):
            result = runner.invoke(main, ["auth", "status"])
            assert "not configured" in result.output.lower()


def test_auth_logout_clears_credentials(tmp_path):
    creds_file = tmp_path / "credentials.json"
    creds_file.write_text("{}")

    runner = CliRunner()
    with patch("ghome.cli.get_credentials_path", return_value=creds_file):
        result = runner.invoke(main, ["auth", "logout"])
        assert result.exit_code == 0
        assert not creds_file.exists()


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
