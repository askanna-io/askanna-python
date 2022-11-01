import sys
from pathlib import Path

import click

from askanna.sdk.run import ArtifactSDK


@click.group()
def cli1():
    pass


@cli1.command(help="Download an artifact of a run", short_help="Download a run artifact")
@click.option("--id", "-i", "run_suuid", prompt="Run SUUID", required=True, type=str, help="Run SUUID")
@click.option(
    "--output", "-o", "output_path", show_default=True, type=click.Path(path_type=Path), help="Filename to save (zip)"
)
def get(run_suuid, output_path):
    """
    Download an artifact of a run
    """

    if not output_path:
        output_path = Path(f"artifact_{run_suuid}.zip")

    if output_path.is_dir():
        click.echo("The output argument is a directory. Please provide a filename (zip) for the output.", err=True)
        sys.exit(1)

    if output_path.exists():
        click.echo(f"The file '{output_path}' already exists. We will not overwrite the existing file.", err=True)
        sys.exit(1)

    click.echo("Downloading the artifact has started...")

    try:
        ArtifactSDK().download(run_suuid, output_path)
    except Exception as e:
        click.echo(f"Something went wrong. The error message received:\n  {e}", err=True)
        sys.exit(1)

    click.echo("We have succesfully downloaded the artifact.")
    click.echo(f"The artifact is saved in: {output_path}")


cli = click.CommandCollection(
    sources=[cli1],
    help="Download artifact of a run",
    short_help="Download run artifact",
)
