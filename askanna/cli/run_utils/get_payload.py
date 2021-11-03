# -*- coding: utf-8 -*-
import os
import sys

import click

from askanna.core.apiclient import client


# read defaults from the environment
default_run_suuid = os.getenv("AA_RUN_SUUID")
default_payload_suuid = os.getenv("AA_PAYLOAD_SUUID")
default_payload_file = os.getenv("AA_PAYLOAD_PATH")

HELP = """Get the payload for the run which is stored in AskAnna"""
SHORT_HELP = "Get payload from AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option("--run", "-r", default=default_run_suuid, show_default=True)
@click.option("--payload", "-p", default=default_payload_suuid, show_default=True)
@click.option(
    "--output", "-o", default=default_payload_file, show_default=True, type=click.Path()
)
def cli(run, payload, output):
    api_server = client.base_url

    # we assume we can get jobrun id and the payload
    payload_url = (
        "{ASKANNA_API_SERVER}runinfo/{RUN_SUUID}/payload/{PAYLOAD_SUUID}/".format(
            RUN_SUUID=run,
            PAYLOAD_SUUID=payload,
            ASKANNA_API_SERVER=api_server,
        )
    )

    req = client.get(payload_url)

    if not req.status_code == 200:
        click.echo(f"Could not retrieve payload with SUUID: {payload}", err=True)
        sys.exit(1)

    if output:
        with open(output, "w") as f:
            f.write(req.text)
    else:
        click.echo(req.text)
