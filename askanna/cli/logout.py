import click

from askanna.config import config

HELP = """
Remove the AskAnna API token that is saved in your global configuration file.
"""

SHORT_HELP = "Remove saved AskAnna API token"


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    config.server.logout_and_remove_token()
    click.echo("You have been logged out!")
