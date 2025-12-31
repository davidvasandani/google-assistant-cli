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
from ghome.assistant import broadcast_message, BroadcastError, send_command, CommandError
from ghome.config import get_client_secret_path, get_credentials_path


@click.group()
@click.version_option(version=__version__)
def main():
    """Google Home CLI - Control Google Home devices from the command line."""
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


@main.command("command")
@click.argument("text", required=False)
@click.option("-i", "--interactive", is_flag=True, help="Interactive shell mode")
@click.option("-v", "--verbose", is_flag=True, help="Show debug output")
def command_cmd(text: str | None, interactive: bool, verbose: bool):
    """Send any command to Google Assistant."""
    try:
        credentials = load_credentials()
    except CredentialsNotFoundError:
        click.echo("Error: Not authenticated.", err=True)
        click.echo("Run 'ghome auth login' first.", err=True)
        sys.exit(1)

    if interactive:
        _run_command_interactive_mode(credentials, verbose)
    elif text:
        _send_single_command(text, credentials, verbose)
    else:
        click.echo("Error: Command text required. Use --interactive for shell mode.", err=True)
        sys.exit(2)


def _send_single_command(text: str, credentials, verbose: bool):
    """Send a single command."""
    try:
        response = send_command(text, credentials)
        click.echo(response)
    except CommandError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(2)
    except Exception as e:
        if verbose:
            click.echo(f"Error: {e}", err=True)
        else:
            click.echo("Error: Failed to send command. Use --verbose for details.", err=True)
        sys.exit(2)


def _run_command_interactive_mode(credentials, verbose: bool):
    """Run interactive command shell."""
    click.echo("Interactive mode. Type 'quit' to exit.")

    while True:
        try:
            text = click.prompt(">", prompt_suffix=" ")
        except (EOFError, KeyboardInterrupt):
            click.echo("\nExiting.")
            break

        if text.lower() in ("quit", "exit", "q"):
            break

        if not text.strip():
            continue

        try:
            response = send_command(text, credentials)
            click.echo(response)
        except CommandError as e:
            click.echo(f"Error: {e}", err=True)
        except Exception as e:
            if verbose:
                click.echo(f"Error: {e}", err=True)
            else:
                click.echo("Error: Failed to send. Use --verbose for details.", err=True)
