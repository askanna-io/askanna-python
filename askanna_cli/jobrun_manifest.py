import os

import click
import requests

from askanna_cli.utils import get_config

HELP = """
JobRun Manifest downloader intended to use in askanna-runner
"""

SHORT_HELP = "Download manifest for jobrun"


@click.option('--output', '-o', default='/entrypoint.sh', show_default=True,
              type=click.Path())
@click.command(help=HELP, short_help=SHORT_HELP)
def cli(output):
    config = get_config()
    token = config['auth']['token']
    api_server = config['askanna']['remote']
    jobrun_short_uuid = os.getenv("JOBRUN_SHORT_UUID")

    download_url = "/".join([
        'jobrun',
        jobrun_short_uuid, 'manifest', ''])
    download_url = api_server + download_url

    headers = {
        'user-agent': 'askanna-cli/0.0.1',
        'Authorization': 'Token {token}'.format(
            token=token
        )
    }

    r = requests.get(download_url, headers=headers)

    with open(output, 'w') as f:
        f.write(r.text)
