# -*- coding: utf-8 -*-
import os
import sys

import click
import requests

from askanna_cli.utils import get_config
# read defaults from the environment
default_jobrun_short_uuid = os.getenv('JOBRUN_SHORT_UUID')
default_payload_uuid = os.getenv('PAYLOAD_UUID')
default_payload_file = os.getenv('PAYLOAD_PATH')


HELP = """
Download the payload stored in AskAnna
"""

SHORT_HELP = "Get payload from AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option('--jobrun', '-j', default=default_jobrun_short_uuid, show_default=True)
@click.option('--payload', '-p', default=default_payload_uuid, show_default=True)
@click.option('--output', '-o', default=default_payload_file, show_default=True,
              type=click.Path())
def cli(jobrun, payload, output):
    config = get_config()
    token = config['auth']['token']
    ASKANNA_API_SERVER = config['askanna']['remote']

    # we assume we can get jobrun id and the payload
    payload_url = "{ASKANNA_API_SERVER}jobrun/{JOBRUN_SHORT_UUID}/payload/{PAYLOAD_UUID}/".format(
        JOBRUN_SHORT_UUID=jobrun,
        PAYLOAD_UUID=payload,
        ASKANNA_API_SERVER=ASKANNA_API_SERVER
    )
    headers = {
        'Authorization': "Token {usertoken}".format(
            usertoken=token
        )
    }

    req = requests.get(
        payload_url,
        headers=headers
    )

    if not req.status_code == 200:
        print("Could't retrieve payload {}".format(payload))
        sys.exit(1)

    if output:
        with open(output, 'w') as f:
            f.write(req.text)
    else:
        print(req.text)
