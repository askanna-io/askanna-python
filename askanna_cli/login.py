import click
# import requests

from askanna_cli.exceptions import AlreadyLoggedInException


HELP = """
Add your AskAnna API key to your global configuration file
(~/.askanna.yml). This is necessary to gain access to projects associated with
your AskAnna account.

You can find your API key in AskAnna WebUI:
    https://askanna.io  #FIXME
"""

SHORT_HELP = "Save your AskAnna API key"


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    click.echo("This is performing the login action")
