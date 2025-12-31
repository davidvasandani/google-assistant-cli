# tests/test_assistant.py
from unittest.mock import patch, MagicMock

import pytest

from ghome.assistant import broadcast_message, BroadcastError, send_command, CommandError


def test_broadcast_message_sends_correct_command():
    mock_assistant = MagicMock()
    mock_assistant.assist.return_value = ("Broadcast sent", None, None)

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


def test_send_command_sends_correct_command():
    mock_assistant = MagicMock()
    mock_assistant.assist.return_value = ("The volume is now 10", None, None)

    with patch("ghome.assistant.TextAssistant") as MockTextAssistant:
        MockTextAssistant.return_value.__enter__.return_value = mock_assistant

        mock_creds = MagicMock()
        result = send_command("set kitchen display volume 10", mock_creds)

        mock_assistant.assist.assert_called_once_with("set kitchen display volume 10")
        assert result == "The volume is now 10"


def test_send_command_raises_on_empty_command():
    mock_creds = MagicMock()

    with pytest.raises(CommandError, match="Command cannot be empty"):
        send_command("", mock_creds)


def test_send_command_returns_default_on_empty_response():
    mock_assistant = MagicMock()
    mock_assistant.assist.return_value = ("", None, None)

    with patch("ghome.assistant.TextAssistant") as MockTextAssistant:
        MockTextAssistant.return_value.__enter__.return_value = mock_assistant

        mock_creds = MagicMock()
        result = send_command("turn off lights", mock_creds)

        assert result == "Command sent"
