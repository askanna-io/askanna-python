import os

import click

from askanna.core.utils import store_config

HELP = """
Remove the AskAnna API key that is saved in your global configuration file
(~/.askanna.yml).
"""

SHORT_HELP = "Forget saved AskAnna API key"


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    new_config = {"auth": {}}
    config = store_config(new_config)
    with open(os.path.expanduser("~/.askanna.yml"), "w") as fd:
        fd.write(config)
    click.echo("You have been logged out!")
