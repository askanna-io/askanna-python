import logging
import sys

import click

from askanna.core.push import push


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

HELP = """
Command to make an ZIP archive of the current working folder.\n
Afterwards we send this ZIP archive to AskAnna.
"""

SHORT_HELP = "Push code to AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option("--force", "-f", is_flag=True, help="Force push")
@click.option(
    "--description",
    "-d",
    required=False,
    type=str,
    help="Add description to this code",
    default="",
)
@click.option(
    "--message",
    "-m",
    required=False,
    type=str,
    help="Add description to this code",
    default="",
)
def cli(force, description, message):
    if len(description) > 0 and len(message) > 0:
        click.echo("Cannot use both --description and --message.", err=True)
        sys.exit(1)
    elif len(message) > 0:
        description = message

    push(force, description)
