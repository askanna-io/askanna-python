import sys
from pathlib import Path

import click

from askanna.gateways.run import RunGateway

HELP = """
Get the run manifest containing the commands to run
"""

SHORT_HELP = "Get manifest for run from AskAnna"


@click.option(
    "--run",
    "run_suuid",
    required=True,
    envvar="AA_RUN_SUUID",
    help="The run SUUID",
)
@click.option(
    "--output",
    "output_path",
    envvar="AA_RUN_MANIFEST_PATH",
    default="/entrypoint.sh",
    show_default=True,
    type=click.Path(path_type=Path),
)
@click.command(help=HELP, short_help=SHORT_HELP)
def cli(run_suuid, output_path):
    try:
        RunGateway().manifest(run_suuid=run_suuid, output_path=output_path, overwrite=True)
    except Exception as e:
        click.echo(f"Something went wrong. The error message received:\n  {e}", err=True)
        sys.exit(1)
