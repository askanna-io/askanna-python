import os
import click

from askanna.core.apiclient import client

HELP = """
Download manifest containing the commands for a run
"""

SHORT_HELP = "Download manifest for run"


@click.option(
    "--output", "-o", default="/entrypoint.sh", show_default=True, type=click.Path()
)
@click.command(help=HELP, short_help=SHORT_HELP)
def cli(output):
    api_server = client.base_url
    run_suuid = os.getenv("AA_RUN_SUUID")

    download_url = "/".join(["runinfo", run_suuid, "manifest", ""])
    download_url = api_server + download_url

    r = client.get(download_url)

    with open(output, "w") as f:
        f.write(r.text)
