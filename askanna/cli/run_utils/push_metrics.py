import click

from askanna.sdk.track import metric_collector

HELP = """
Retrieve metrics generated with track_metric(s) and push these metrics to AskAnna
"""

SHORT_HELP = "Push metrics to AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option("--force", "-f", is_flag=True, help="Force push metrics")
def cli(force):
    if len(metric_collector) > 0 or force:
        metric_collector.save(force=True)
