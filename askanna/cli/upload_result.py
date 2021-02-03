# -*- coding: utf-8 -*-
import os
import sys
import click

from askanna.core.utils import scan_config_in_path
from askanna.core.utils import get_config
from askanna.core.upload import ResultUpload

HELP = """
After a run, we can store the result in AskAnna
"""

SHORT_HELP = "Upload the result from a run"


def create_jobresult(jobname: str, cwd: str) -> str:
    config = get_config()

    paths = config[jobname].get('output', {}).get('result')

    if isinstance(paths, list):
        print("Please enter a path in output/result, not a list")
        sys.exit(1)

    return paths


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    config = get_config()
    token = config['auth']['token']
    api_server = config['askanna']['remote']
    project = config.get('project', {})
    project_uuid = project.get('uuid')

    jobrun_uuid = os.getenv('JOBRUN_UUID')
    jobrun_suuid = os.getenv('JOBRUN_SUUID')
    jobrun_jobname = os.getenv('JOBRUN_JOBNAME')

    result_uuid = os.getenv('RESULT_UUID')
    result_suuid = os.getenv('RESULT_SUUID')

    # first check whether we need to create artifacts or not
    # if output is not specifed
    # or if output.paths is not specified
    # then we skip this step and report this to the stdout

    result_defined = config[jobrun_jobname].get('output', {}).get('result')

    if not result_defined:
        print("Result storage aborted, no `output/result` defined for this job in `askanna.yml`")
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

    # First check whether we have a result defined
    paths = config[jobrun_jobname].get('output', {}).get('result')
    if not paths:
        print("No output was defined in output/result, not uploading to AskAnna")
        sys.exit(0)

    jobresult_archive = create_jobresult(jobname=jobrun_jobname, cwd=upload_folder)

    click.echo("Uploading result to AskAnna...")

    fileinfo = {
        "filename": os.path.basename(jobresult_archive),
        "size": os.stat(jobresult_archive).st_size,
    }
    uploader = ResultUpload(
        token=token,
        api_server=api_server,
        project_uuid=project_uuid,
        JOBRUN_UUID=jobrun_uuid,
        JOBRUN_SUUID=jobrun_suuid,
        RESULT_UUID=result_uuid,
        RESULT_SUUID=result_suuid,
    )
    status, msg = uploader.upload(jobresult_archive, config, fileinfo)
    if status:
        print(msg)
        sys.exit(0)
    else:
        print(msg)
        sys.exit(1)
