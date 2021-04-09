import logging
import click
from askanna.core.variables_tracked import vc

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

HELP = """
Retrieve variables generated with track_variable(s) and push variables to AskAnna
"""

SHORT_HELP = "Push variables to AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option("--force", "-f", is_flag=True, help="Force push variables")
def cli(force):
    if vc.has_variables() or force:
        vc.save(force=True)
