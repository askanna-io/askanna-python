# -*- coding: utf-8 -*-
import os
import sys
import click

from askanna.core import client as askanna_client
from askanna.core.download import ChunkedDownload
from askanna.core.utils import content_type_file_extension


@click.group()
def cli1():
    pass


@cli1.command(
    help="Download a result of a run", short_help="Download a run result"
)
@click.option("--id", "-i", "suuid", prompt='Run SUUID', required=True, type=str, help="Run SUUID")
@click.option("--output", "-o", "output_path", show_default=True, type=click.Path(), help="File name to save result")
def get(suuid, output_path):
    """
    Download a result of a run
    """
    result_url = f"{askanna_client.config.remote}result/{suuid}/"
    stable_download = ChunkedDownload(result_url)

    if stable_download.status_code != 200:
        click.echo(f"{stable_download.status_code} - We cannot find this result for you", err=True)
        sys.exit(1)

    if not output_path:
        file_extension = content_type_file_extension(str(stable_download.content_type))
        output_path = f"result_{suuid}{file_extension}"

    if os.path.isdir(output_path):
        click.echo(
            "The output argument is a directory. Please provide a file name for the output.",
            err=True
        )
        sys.exit(1)

    if os.path.exists(output_path):
        click.echo(
            "The output file already exists. We will not overwrite the existing file.",
            err=True
        )
        sys.exit(1)

    click.echo("Downloading the result has started...")
    stable_download.download(output_file=output_path)
    click.echo("We have succesfully downloaded the result.")
    click.echo(f"The result is saved in: {output_path}")


cli = click.CommandCollection(
    sources=[cli1],
    help="Download result of a run",
    short_help="Download run result",
)
