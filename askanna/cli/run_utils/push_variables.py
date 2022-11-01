import click

from askanna.sdk.track import variable_collector

HELP = """
Retrieve variables generated with track_variable(s) and push variables to AskAnna
"""

SHORT_HELP = "Push variables to AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option("--force", "-f", is_flag=True, help="Force push variables")
def cli(force):
    if len(variable_collector) > 0 or force:
        variable_collector.save(force=True)
