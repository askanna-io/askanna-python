import sys

import click

from askanna import project
from askanna.config import config
from askanna.core.push import is_project_config_push_ready, push

HELP = """
Command to make an ZIP archive of the current working folder.
Afterwards we upload (push) this ZIP archive to AskAnna.
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

    if not is_project_config_push_ready():
        sys.exit(1)

    # Check for existing package
    if not force:
        packages = project.packages(config.project.project_suuid, offset=0, limit=1)
        if packages and not click.confirm("Do you want to replace the current code on AskAnna?"):
            click.echo("We are not pushing your code to AskAnna. You choose not to replace your existing code.")
            sys.exit(0)

    push(overwrite=True, description=description or message)
