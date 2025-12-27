"""Command-line interface for Google Home CLI."""

import click

from ghome import __version__


@click.group()
@click.version_option(version=__version__)
def main():
    """Google Home CLI - Broadcast messages to Google Home devices."""
    pass
