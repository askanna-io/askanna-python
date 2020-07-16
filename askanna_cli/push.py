
import os
import re
import sys
import uuid

import click
import git
import requests

from askanna_cli.utils import zipFilesInDir, scan_config_in_path
from askanna_cli.utils import get_config
from askanna_cli.core.upload import PackageUpload

HELP = """
Wrapper command to push the current working folder to archive.\n
Afterwards we send this to AskAnna
"""

SHORT_HELP = "Push code to AskAnna"


def package(src: str) -> str:

    pwd_dir_name = os.path.basename(src)
    random_suffix = uuid.uuid4().hex

    random_name = os.path.join(
        "/", "tmp", "{pwd_dir_name}_{random_suffix}.zip".format(
            pwd_dir_name=pwd_dir_name,
            random_suffix=random_suffix
        ))

    zipFilesInDir(src, random_name, lambda x: x)
    return random_name


def extract_push_target(push_target):
    """
    Extract push target from the url configured
    Workspace is optional
    """
    match_pattern = re.compile(r"(?P<http_scheme>https|http):\/\/(?P<askanna_host>[\w\.\-\:]+)\/(?P<workspace_suuid>[\w-]+){0,1}\/{0,1}project\/(?P<project_suuid>[\w-]+)\/{0,1}")  # noqa
    matches = match_pattern.match(push_target)
    matches_dict = matches.groupdict()
    return matches_dict


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option('--message', '-m', default='', type=str, help='Add description to this code')
def cli(message):
    config = get_config()
    token = config['auth']['token']
    api_server = config['askanna']['remote']
    project = config.get('project', {})
    project_uuid = project.get('uuid')

    # read and parse the push-target from askanna
    push_target = config.get('push-target')

    if not push_target:
        print("`push-target` is not set, please set the `push-target` in order to push to AskAnna")
        sys.exit(1)

    matches_dict = extract_push_target(push_target)
    api_host = matches_dict.get("askanna_host")
    http_scheme = matches_dict.get("http_scheme")
    if api_host:
        # first also modify the first part
        if api_host.startswith('localhost'):
            api_host = api_host
        elif api_host not in ['askanna.eu']:
            first_part = api_host.split('.')[0]
            last_part = api_host.split('.')[1:]
            api_host = ".".join(
                [first_part+"-api"]+last_part
            )
        else:
            api_host = 'api.' + api_host
        api_server = "{}://{}/v1/".format(http_scheme, api_host)
    project_suuid = matches_dict.get("project_suuid")

    if project_suuid:
        # make an extra call to askanna to query for the full uuid for this project
        r = requests.get(
            "{api_server}project/{project_suuid}/".format(
                api_server=api_server,
                project_suuid=project_suuid
            ),
            headers={
                'user-agent': 'askanna-cli/0.2.0',
                'Authorization': 'Token {token}'.format(
                    token=token
                )
            }
        )
        if not r.status_code == 200:
            print("Couldn't find specified project {}".format(push_target))
            sys.exit(1)
        j = r.json()
        project_uuid = j.get('uuid')

    if not project_uuid:
        print("Cannot upload unregistered project to AskAnna")
        sys.exit(1)

    cwd = os.getcwd()

    upload_folder = cwd
    askanna_config = scan_config_in_path()
    project_folder = os.path.dirname(askanna_config)

    def ask_which_folder(cwd, project_folder) -> str:
        confirm = input("Proceed upload [c]urrent or [p]roject folder? : ")
        answer = confirm.strip()
        if answer not in ['c', 'p']:
            return ask_which_folder(cwd, project_folder)
        if confirm == 'c':
            return cwd
        if confirm == 'p':
            return project_folder

    if not cwd == project_folder:
        print("You are not at the root folder of the project '{}'".format(project_folder))
        upload_folder = ask_which_folder(cwd, project_folder)

    package_archive = package(upload_folder)

    # attach message to this package upload
    if not message:
        # try git
        try:
            repo = git.Repo(".")
        except Exception as e:
            print(e)
        else:
            commit = repo.head.commit
            message = commit.message

    click.echo("Uploading '{}' to AskAnna...".format(upload_folder))

    fileinfo = {
        "filename": os.path.basename(package_archive),
        "size": os.stat(package_archive).st_size,
    }
    uploader = PackageUpload(
        token=token,
        api_server=api_server,
        project_uuid=project_uuid,
        description=message
    )
    status, msg = uploader.upload(package_archive, config, fileinfo)
    if status:
        print(msg)
        sys.exit(0)
    else:
        print(msg)
        sys.exit(1)
