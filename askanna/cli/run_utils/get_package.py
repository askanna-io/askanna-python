import os
import sys

import click
from zipfile import ZipFile

from askanna.core.apiclient import client


HELP = """
Package downloader, intended for use with runner and unpacks code to /code
"""

SHORT_HELP = "Download package code for AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    api_server = client.base_url
    project_suuid = os.getenv("AA_PROJECT_SUUID")
    package_suuid = os.getenv("AA_PACKAGE_SUUID")

    if not project_suuid:
        click.echo("No AA_PROJECT_SUUID found.", err=True)
        sys.exit(1)
    if not package_suuid:
        click.echo("No AA_PACKAGE_SUUID found.", err=True)
        sys.exit(1)

    download_url = "/".join(
        ["project", project_suuid, "packages", package_suuid, "download", ""]
    )
    download_url = api_server + download_url

    r = client.get(download_url)
    res = r.json()

    r = client.get(res["target"])
    with open("/tmp/code.zip", "wb") as f:
        f.write(r.content)

    with ZipFile("/tmp/code.zip", "r") as myzip:
        myzip.extractall("/code")
