import sys
from pathlib import Path

import click

from askanna.gateways.run import RunGateway

HELP = """Get the payload for the run from AskAnna and it to a file."""
SHORT_HELP = "Get payload from AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option(
    "--run",
    "run_suuid",
    required=True,
    envvar="AA_RUN_SUUID",
    help="The run SUUID",
)
@click.option(
    "--payload",
    "payload_suuid",
    required=True,
    envvar="AA_PAYLOAD_SUUID",
    help="The payload SUUID",
)
@click.option(
    "--output",
    "output_path",
    envvar="AA_PAYLOAD_PATH",
    default="/input/payload.json",
    show_default=True,
    type=click.Path(path_type=Path),
)
def cli(run_suuid, payload_suuid, output_path):
    try:
        RunGateway().payload(run_suuid, payload_suuid, output_path)
    except Exception as e:
        click.echo(f"Something went wrong getting the payload. The error message received:\n  {e}", err=True)
        sys.exit(1)
