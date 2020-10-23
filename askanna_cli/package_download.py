import os

import click
import requests
from zipfile import ZipFile

from askanna_cli.utils import get_config

HELP = """
Package downloader, intended for use with runner and unpacks code to /code
"""

SHORT_HELP = "Download package code for askanna"


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    config = get_config()
    token = config['auth']['token']
    api_server = config['askanna']['remote']
    project_suuid = os.getenv('PROJECT_SUUID')
    package_suuid = os.getenv('PACKAGE_SUUID')

    download_url = "/".join([
        'project',
        project_suuid, 'packages',
        package_suuid, 'download', ''])
    download_url = api_server + download_url

    headers = {
        'user-agent': 'askanna-cli/0.3.1',
        'Authorization': 'Token {token}'.format(
            token=token
        )
    }

    r = requests.get(download_url, headers=headers)
    res = r.json()

    r = requests.get(res['target'], headers=headers)
    with open('/tmp/code.zip', 'wb') as f:
        f.write(r.content)

    with ZipFile('/tmp/code.zip', 'r') as myzip:
        myzip.extractall('/code')
