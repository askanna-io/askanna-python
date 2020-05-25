import click

HELP = """
Remove the AskAnna API key that is saved in your global configuration file
(~/.askanna.yml) if any.
"""

SHORT_HELP = "Forget saved AskAnna API key"


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    click.echo("This is performing the logout action")
