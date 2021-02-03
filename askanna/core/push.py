import os
import sys
import tempfile
import uuid

import click
import git

from askanna.core.utils import zipFilesInDir, scan_config_in_path
from askanna.core.utils import get_config, getProjectInfo, getProjectPackages
from askanna.core.utils import extract_push_target
from .upload import PackageUpload


def package(src: str) -> str:

    pwd_dir_name = os.path.basename(src)
    random_suffix = uuid.uuid4().hex

    # make a temporary directory
    tmpdir = tempfile.mkdtemp(prefix="askanna-package")

    random_name = os.path.join(
        tmpdir, "{pwd_dir_name}_{random_suffix}.zip".format(
            pwd_dir_name=pwd_dir_name,
            random_suffix=random_suffix
        ))

    zipFilesInDir(src, random_name, lambda x: x)
    return random_name


def push(force: bool, message: str = None):
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
        project_info = getProjectInfo(project_suuid)
        if project_info.uuid is None:
            print("Couldn't find specified project {}".format(push_target))
            sys.exit(1)

        project_uuid = project_info.uuid

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
    packages = getProjectPackages(project_info)
    if packages['count'] > 0:
        # ask for confirmation if `-f` flag is not set
        overwrite = force
        if not force:
            overwrite = ask_overwrite()

        if not overwrite:
            print("We are not pushing your code to AskAnna. You choose not to replace your "
                  "existing code.")
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
        # remove temporary zip-file from the system including the parent temporary folder
        try:
            os.remove(package_archive)
            os.rmdir(os.path.dirname(package_archive))
            print("Successfully pushed the project to AskAnna!")
        except OSError as e:
            print("Pushing your code was successful, but we could not remove the temporary file "
                  "used for uploading your code to AskAnna.")
            print("The error: {}".format(e.strerror))
            print("You can manually delete the file: {}".format(package_archive))
    else:
        print(msg)
        sys.exit(1)
