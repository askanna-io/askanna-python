import click


HELP = """
This command will allow you to perform a run on a remote
location for the particular project.
"""

SHORT_HELP = "Execute run of deployed AskAnna project"


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    click.echo("Execution of remote Run")
