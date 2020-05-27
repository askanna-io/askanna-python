
import os
import sys

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
    project = config.get('project', {})
    project_uuid = project.get('uuid')
    project_short_uuid = os.getenv('PROJECT_SHORT_UUID')
    package_uuid = os.getenv('PACKAGE_UUID')

    if not project_uuid:
        print("Cannot download project from AskAnna")
        sys.exit(1)

    download_url = "/".join([
        'project',
        project_short_uuid, 'packages',
        package_uuid, 'download', ''])
    download_url = api_server + download_url

    headers = {
        'user-agent': 'askanna-cli/0.0.1',
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
