import os
import sys
from tempfile import gettempdir
from zipfile import ZipFile

import click

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
    code_dir = os.getenv("AA_CODE_DIR", "/code")

    temp_path = f"{gettempdir()}/askanna"
    temp_package_file = f"{temp_path}/code.zip"
    os.makedirs(temp_path, exist_ok=True)

    if not project_suuid:
        click.echo("No AA_PROJECT_SUUID found.", err=True)
        sys.exit(1)
    if not package_suuid:
        click.echo("No AA_PACKAGE_SUUID found.", err=True)
        sys.exit(1)

    download_url = "/".join(["project", project_suuid, "packages", package_suuid, "download", ""])
    download_url = api_server + download_url

    r = client.get(download_url)

    if r.status_code == 404:
        click.echo("This package does not exist.", err=True)
        sys.exit(1)

    res = r.json()
    r = client.get(res["target"])

    with open(temp_package_file, "wb") as f:
        f.write(r.content)

    with ZipFile(temp_package_file, "r") as myzip:
        myzip.extractall(code_dir)
