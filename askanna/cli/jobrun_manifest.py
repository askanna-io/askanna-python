import os

import click
import requests

from askanna.core.utils import get_config

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
    jobrun_suuid = os.getenv("JOBRUN_SUUID")

    download_url = "/".join([
        'jobrun',
        jobrun_suuid, 'manifest', ''])
    download_url = api_server + download_url

    headers = {
        'user-agent': 'askanna-cli/0.3.0',
        'Authorization': 'Token {token}'.format(
            token=token
        )
    }

    r = requests.get(download_url, headers=headers)

    with open(output, 'w') as f:
        f.write(r.text)
