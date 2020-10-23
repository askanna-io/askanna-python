import json
import logging
import os
import re
import sys
import uuid

import click
import git

from askanna_cli import config_dirs
from askanna_cli.utils import zipFilesInDir, scan_config_in_path
from askanna_cli.utils import get_config, getProjectInfo, getProjectPackages
from askanna_cli.core.upload import PackageUpload

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

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


def check_existing_package(project, push_target, upload_folder, api_server, token) -> bool:

    # check existence the usercache folder
    askanna_folder = config_dirs.user_cache_dir
    if not(os.path.exists(
        askanna_folder
    ) and os.path.isdir(askanna_folder)):
        packages = getProjectPackages(project, api_server, token)
        return len(packages) > 0
    # read contents from .askanna folder
    try:
        with open(os.path.join(
            askanna_folder,
            'PACKAGE-INFO'
        )) as f:
            j = json.loads(f.read())
    except Exception as e:
        # information is not there
        # please retrieve this info from askanna
        logging.debug(e)
        packages = getProjectPackages(project, api_server, token)
        return len(packages) > 0
    else:
        if push_target in j.keys():
            return True
        else:
            return False

    return True


def writePackageInfo(project, push_target, upload_folder):
    askanna_folder = config_dirs.user_cache_dir
    os.makedirs(askanna_folder, exist_ok=True)

    # does the file exist? create one if not

    try:
        with open(os.path.join(askanna_folder, 'PACKAGE-INFO')) as f:
            j = json.loads(f.read())
    except Exception:
        with open(os.path.join(askanna_folder, 'PACKAGE-INFO'), 'w') as f:
            f.write(json.dumps({
                push_target: project
            }, indent=2))
    else:
        with open(os.path.join(askanna_folder, 'PACKAGE-INFO'), 'w') as f:
            j.update(**{
                push_target: project
            })
            f.write(json.dumps(j, indent=2))


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
@click.option('--force', '-f', is_flag=True, help='Force push')
@click.option('--message', '-m', default='', type=str, help='Add description to this code')
def cli(force, message):
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

    project_info = {}
    if project_suuid:
        # make an extra call to askanna to query for the full uuid for this project
        project_info = getProjectInfo(project_suuid, api_server, token)
        if project_info == {}:
            print("Couldn't find specified project {}".format(push_target))
            sys.exit(1)

        project_uuid = project_info.get('uuid')

    if not project_uuid:
        print("Cannot upload unregistered project to AskAnna")
        sys.exit(1)

    def ask_overwrite() -> bool:
        confirm = input("Do you want to replace the current code on AskAnna? [y/n]: ")
        answer = confirm.strip()
        if answer not in ['n', 'y']:
            print("Invalid option selected, choose from: y or n")
            return ask_overwrite()
        if confirm == 'y':
            return True
        else:
            return False

    cwd = os.getcwd()

    upload_folder = cwd
    askanna_config = scan_config_in_path()
    project_folder = os.path.dirname(askanna_config)

    def ask_which_folder(cwd, project_folder) -> str:
        confirm = input("Proceed upload [c]urrent or [p]roject folder? : ")
        answer = confirm.strip()
        if answer not in ['c', 'p']:
            print("Invalid option selected, choose from: c or p")
            return ask_which_folder(cwd, project_folder)
        if confirm == 'c':
            return cwd
        if confirm == 'p':
            return project_folder

    if not cwd == project_folder:
        print("You are not at the root folder of the project '{}'".format(project_folder))
        upload_folder = ask_which_folder(cwd, project_folder)

    # check for existing package
    if check_existing_package(project_info, push_target, upload_folder, api_server, token):
        # ask for confirmation if `-f` flag is not set
        overwrite = force
        if not force:
            overwrite = ask_overwrite()

        if not overwrite:
            print("We are not pushing your code to AskAnna. You choose not to replace your existing code.")
            sys.exit(0)

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

    # if there is still no message set then use the zipfilename
    if not message:
        message = os.path.basename(package_archive)

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

        # create log that this package was uploaded once
        writePackageInfo(project_info, push_target, upload_folder)
        sys.exit(0)
    else:
        print(msg)
        sys.exit(1)
