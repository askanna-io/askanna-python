import click


HELP = """
This command will allow you to create a project
"""

SHORT_HELP = "Create an AskAnna project"


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    click.echo("This is performing the createproject action")
