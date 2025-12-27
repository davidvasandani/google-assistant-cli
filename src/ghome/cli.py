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
from ghome.config import get_client_secret_path, get_credentials_path


@click.group()
@click.version_option(version=__version__)
def main():
    """Google Home CLI - Broadcast messages to Google Home devices."""
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
