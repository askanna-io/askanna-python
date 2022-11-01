import sys
from pathlib import Path

import click

from askanna import result


@click.group()
def cli1():
    pass


@cli1.command(help="Download a result of a run", short_help="Download a run result")
@click.option("--id", "-i", "run_suuid", prompt="Run SUUID", required=True, type=str, help="Run SUUID")
@click.option("--output", "-o", "output_path", type=click.Path(path_type=Path), help="Filename for the result")
def get(run_suuid, output_path):
    """
    Download a result of a run
    """
    if not output_path:
        filename = result.get_filename(run_suuid)
        output_path = Path(f"result_{run_suuid}_{filename}")

    if output_path.is_dir():
        click.echo("The output argument is a directory. Please provide a filename for the output.", err=True)
        sys.exit(1)

    if output_path.exists():
        click.echo(f"The file '{output_path}' already exists. We will not overwrite the existing file.", err=True)
        sys.exit(1)

    click.echo("Downloading the result has started...")

    try:
        result.download(run_suuid, output_path)
    except Exception as e:
        click.echo(f"Something went wrong while downloading the result:\n  {e}", err=True)
        sys.exit(1)

    click.echo("We have succesfully downloaded the result.")
    click.echo(f"The result is saved in: {output_path}")


cli = click.CommandCollection(
    sources=[cli1],
    help="Download result of a run",
    short_help="Download run result",
)
