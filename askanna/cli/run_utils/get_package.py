import io
import sys
from pathlib import Path
from zipfile import ZipFile

import click

from askanna.sdk.package import PackageSDK

HELP = """
Get the code package for the run from AskAnna. Intended for use with runner and unpacks the package to a directory.
"""
SHORT_HELP = "Get code package from AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option(
    "--package",
    "package_suuid",
    required=True,
    envvar="AA_PACKAGE_SUUID",
    type=str,
    help="The package SUUID",
)
@click.option(
    "--output",
    "output_dir",
    envvar="AA_CODE_DIR",
    default="/code",
    show_default=True,
    type=click.Path(path_type=Path),
)
def cli(package_suuid, output_dir):

    try:
        package_content = PackageSDK().get(package_suuid)
    except Exception as e:
        click.echo(f"Something went wrong getting the package. The error message received:\n  {e}", err=True)
        sys.exit(1)

    if not package_content:
        click.echo(f"No files found for package SUUID '{package_suuid}'", err=True)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    with ZipFile(io.BytesIO(package_content), "r") as zip_file:
        zip_file.extractall(output_dir)
