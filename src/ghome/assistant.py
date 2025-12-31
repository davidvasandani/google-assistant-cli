"""Google Assistant interaction."""

import google.oauth2.credentials
from gassist_text import TextAssistant


class BroadcastError(Exception):
    """Raised when broadcast fails."""
    pass


class CommandError(Exception):
    """Raised when a command fails."""
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
        response_text, _, _ = assistant.assist(command)

    return response_text or "Broadcast sent"


def send_command(
    command: str,
    credentials: google.oauth2.credentials.Credentials,
) -> str:
    """Send any command to Google Assistant."""
    command = command.strip()

    if not command:
        raise CommandError("Command cannot be empty")

    with TextAssistant(credentials) as assistant:
        response_text, _, _ = assistant.assist(command)

    return response_text or "Command sent"
