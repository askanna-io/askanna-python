# -*- coding: utf-8 -*-
import os
import sys
import time
from zipfile import ZipFile
import requests
import click

from askanna_cli.utils import zipPaths
from askanna_cli.utils import scan_config_in_path
from askanna_cli.utils import get_config, string_expand_variables
from askanna_cli.core.upload import ArtifactUpload


@click.group()
def cli1():
    pass


@click.group()
def cli2():
    pass


def create_artifact(jobname: str, cwd: str) -> str:
    config = get_config()

    paths = config[jobname].get('output', {}).get('paths')

    # expand and translate paths if they are configured with variables
    paths = string_expand_variables(paths)

    zipFileName = '/tmp/artifact.zip'
    with ZipFile(zipFileName, mode='w') as zipObj:
        zipPaths(zipObj, paths, cwd)

    return zipFileName


@cli1.command(help="After a run of a job, we can save job run artifacts to an archive",
              short_help="Save artifact from a job run")
def add():
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


@cli2.command(help="Download an artifact of a job run", short_help="Download a job run artifact")
@click.option('--id', '-i', required=True, type=str, help='Job run SUUID')
@click.option('--output', '-o', show_default=True, type=click.Path())
def get(id, output):
    """
    Download an artifact of a job run
    """

    config = get_config()
    token = config['auth']['token']
    ASKANNA_API_SERVER = config.get('askanna', {}).get('remote')

    base_url = "{server}".format(server=ASKANNA_API_SERVER)
    url = base_url + "artifact/{}".format(id)

    headers = {
        'user-agent': 'askanna-cli/0.2.1',
        'Authorization': "Token {token}".format(token=token)
    }

    r = requests.get(url, headers=headers, stream=True)
    if r.status_code != 200:
        print("We cannot find this artifact for you")
        sys.exit(1)

    if not output:
        output = "artifact_{suuid}_{datetime}.zip".format(suuid=id, datetime=time.strftime("%Y%m%d-%H%M%S"))

    if os.path.exists(output):
        print("The output file already exists. We will not overwrite the existing file.")
        sys.exit(1)

    with open(output, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)

    print("We have succesfully downloaded the job run artifact.")
    print("The artifact is saved in: {file}".format(file=output))


cli = click.CommandCollection(sources=[cli1, cli2], help="Save and download job run artifacts",
                              short_help="Save and download job run artifacts")
