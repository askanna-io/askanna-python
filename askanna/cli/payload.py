# -*- coding: utf-8 -*-
import os
import sys

import click

from askanna.core import client as askanna_client
from askanna.core.utils import get_config


# read defaults from the environment
default_jobrun_suuid = os.getenv('JOBRUN_SUUID')
default_payload_suuid = os.getenv('PAYLOAD_SUUID')
default_payload_file = os.getenv('PAYLOAD_PATH')

HELP = """
Download the payload stored in AskAnna
"""

SHORT_HELP = "Get payload from AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option('--jobrun', '-j', default=default_jobrun_suuid, show_default=True)
@click.option('--payload', '-p', default=default_payload_suuid, show_default=True)
@click.option('--output', '-o', default=default_payload_file, show_default=True,
              type=click.Path())
def cli(jobrun, payload, output):
    config = get_config()
    ASKANNA_API_SERVER = config['askanna']['remote']

    # we assume we can get jobrun id and the payload
    payload_url = "{ASKANNA_API_SERVER}jobrun/{JOBRUN_SUUID}/payload/{PAYLOAD_SUUID}/".format(
        JOBRUN_SUUID=jobrun,
        PAYLOAD_SUUID=payload,
        ASKANNA_API_SERVER=ASKANNA_API_SERVER
    )

    req = askanna_client.get(
        payload_url
    )

    if not req.status_code == 200:
        print("Could't retrieve payload {}".format(payload))
        sys.exit(1)

    if output:
        with open(output, 'w') as f:
            f.write(req.text)
    else:
        print(req.text)
