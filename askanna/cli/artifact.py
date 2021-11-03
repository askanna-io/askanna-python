# -*- coding: utf-8 -*-
import os
import sys
import click

from askanna.core.apiclient import client
from askanna.core.download import ChunkedDownload


@click.group()
def cli1():
    pass


@cli1.command(
    help="Download an artifact of a run", short_help="Download a run artifact"
)
@click.option("--id", "-i", "suuid", prompt='Run SUUID', required=True, type=str, help="Run SUUID")
@click.option("--output", "-o", "output_path", show_default=True, type=click.Path(), help="File name to save (zip)")
def get(suuid, output_path):
    """
    Download an artifact of a run
    """
    url = f"{client.base_url}artifact/{suuid}/"

    if not output_path:
        output_path = f"artifact_{suuid}.zip"

    if os.path.isdir(output_path):
        click.echo(
            "The output argument is a directory. Please provide a file name (zip) for the output.",
            err=True
        )
        sys.exit(1)

    if os.path.exists(output_path):
        click.echo(
            "The output file already exists. We will not overwrite the existing file.",
            err=True,
        )
        sys.exit(1)

    stable_download = ChunkedDownload(url=url)
    if stable_download.status_code != 200:
        click.echo("We cannot find this artifact for you.", err=True)
        sys.exit(1)
    click.echo("Downloading the artifact has started...")
    stable_download.download(output_file=output_path)
    click.echo("We have succesfully downloaded the artifact.")
    click.echo(f"The artifact is saved in: {output_path}")


cli = click.CommandCollection(
    sources=[cli1],
    help="Download artifact of a run",
    short_help="Download run artifact",
)
