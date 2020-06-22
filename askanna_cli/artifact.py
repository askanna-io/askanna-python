# -*- coding: utf-8 -*-
import os
import sys
from zipfile import ZipFile
import click

from askanna_cli.utils import zipPaths
from askanna_cli.utils import scan_config_in_path
from askanna_cli.utils import get_config, string_expand_variables
from askanna_cli.core.upload import ArtifactUpload

HELP = """
After a jobrun, we can add outputfiles to an archinve (artifact)
"""

SHORT_HELP = "Create artifact from jobrun"


def create_artifact(jobname: str, cwd: str) -> str:
    config = get_config()

    paths = config[jobname].get('output', {}).get('paths')

    # expand and translate paths if they are configured with variables
    paths = string_expand_variables(paths)

    zipFileName = '/tmp/artifact.zip'
    with ZipFile(zipFileName, mode='w') as zipObj:
        zipPaths(zipObj, paths, cwd)

    return zipFileName


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    config = get_config()
    token = config['auth']['token']
    api_server = config['askanna']['remote']

    project_uuid = os.getenv('PROJECT_UUID')
    project_suuid = os.getenv('PROJECT_SUUID')

    jobrun_suuid = os.getenv('JOBRUN_SUUID')
    jobrun_jobname = os.getenv('JOBRUN_JOBNAME')

    if not project_suuid:
        print("Cannot upload unregistered project to AskAnna")
        sys.exit(1)

    # first check whether we need to create artifacts or not
    # if output is not specifed
    # or if output.paths is not specified
    # then we skip this step and report this to the stdout

    output_defined = config[jobrun_jobname].get('output')
    paths_defined = config[jobrun_jobname].get('output', {}).get('paths')

    if None in [output_defined, paths_defined]:
        print("Artifact creation aborted, no `output` or `output/paths` defined in `askanna.yml`")
        sys.exit(0)

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
        print("You are not at the root folder of the project '{}'".format(
            project_folder))
        upload_folder = ask_which_folder(cwd, project_folder)

    artifact_archive = create_artifact(jobname=jobrun_jobname, cwd=upload_folder)

    click.echo("Uploading artifact to AskAnna...")

    fileinfo = {
        "filename": os.path.basename(artifact_archive),
        "size": os.stat(artifact_archive).st_size,
    }
    uploader = ArtifactUpload(
        token=token,
        api_server=api_server,
        project_uuid=project_uuid,
        JOBRUN_SUUID=jobrun_suuid
    )
    status, msg = uploader.upload(artifact_archive, config, fileinfo)
    if status:
        print(msg)
        sys.exit(0)
    else:
        print(msg)
        sys.exit(1)
