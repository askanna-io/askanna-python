import click
from cookiecutter.main import cookiecutter

# FIXME: this will be an AskAnna public link in the future
# For dev purposes, add your local path to the cookiecutter template
ASKANNA_BASEDSP = "https://gitlab.askanna.io/askanna/cookiecutter-askannabasedsp.git"
ASKANNA_BASEDSP = "git@gitlab.askanna.io:askanna/cookiecutter-askannabasedsp.git"

HELP = """
This command will allow you to create a project
"""

SHORT_HELP = "Create an AskAnna project"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.argument("template", required=False, default="basedsp")
def cli(template):
    click.echo("This is performing the createproject action")

    if template and template == "basedsp" or "base":
        cookiecutter(ASKANNA_BASEDSP)
