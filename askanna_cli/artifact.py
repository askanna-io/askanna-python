import glob
import io
import os
import shutil
import subprocess
import sys
import uuid
import zipfile
from zipfile import ZipFile

import click
import requests
import resumable

from askanna_cli.utils import check_for_project, zipFilesInDir, _file_type, diskunit, scan_config_in_path
from askanna_cli.utils import init_checks, get_config, store_config
from askanna_cli.core.upload import Upload, PackageUpload, ArtifactUpload

HELP = """
Wrapper command to package the current working folder to archive
Afterwards we send this to the ASKANNA_FILEUPLOD_ENDPOINT
"""

SHORT_HELP = "Package code for askanna"


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


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    config = get_config()
    token = config['auth']['token']
    api_server = config['askanna']['remote']
    project = config.get('project', {})
    project_uuid = project.get('uuid')

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

    click.echo("Uploading '{}' to AskAnna...".format(upload_folder))

    fileinfo = {
        "filename": os.path.basename(package_archive),
        "size": os.stat(package_archive).st_size,
    }
    uploader = ArtifactUpload(
        token=token,
        api_server=api_server,
        project_uuid=project_uuid,
        JOBRUN_SHORT_UUID='5B4O-Gaob-LqcG-dpf7'
    )
    status, msg = uploader.upload(package_archive, config, fileinfo)
    if status:
        print(msg)
        sys.exit(0)
    else:
        print(msg)
        sys.exit(1)
