import logging
import click
from askanna.core.metrics import mc

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

HELP = """
Retrieve metrics generated with track_metric and push metrics to AskAnna
"""

SHORT_HELP = "Push metrics to AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option("--force", "-f", is_flag=True, help="Force push metrics")
def cli(force):
    if mc.has_metrics() or force:
        mc.save(force=True)
