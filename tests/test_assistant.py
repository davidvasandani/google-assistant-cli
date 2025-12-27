# tests/test_assistant.py
from unittest.mock import patch, MagicMock

import pytest

from ghome.assistant import broadcast_message, BroadcastError


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
