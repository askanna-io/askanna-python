# -*- coding: utf-8 -*-
import os
import sys
import click

from askanna.core.utils import scan_config_in_path
from askanna.core.utils import get_config
from askanna.core.upload import ResultUpload

HELP = """
At the end of a run push the result to AskAnna
"""

SHORT_HELP = "Push result to AskAnna"


def create_jobresult(jobname: str, cwd: str) -> str:
    config = get_config()

    paths = config[jobname].get("output", {}).get("result")

    if isinstance(paths, list):
        click.echo("Please enter a path in `output/result`, not a list", err=True)
        sys.exit(1)

    return paths


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    config = get_config()
    api_server = config["askanna"]["remote"]

    run_suuid = os.getenv("AA_RUN_SUUID")
    job_name = os.getenv("AA_JOB_NAME")

    result_suuid = os.getenv("AA_RESULT_SUUID")

    # first check whether we need to create artifacts or not
    # if output is not specifed
    # or if output.paths is not specified
    # then we skip this step and report this to the stdout

    result_defined = config[job_name].get("output", {}).get("result")

    if not result_defined:
        click.echo(
            "Result storage aborted, no `output/result` defined for this job in `askanna.yml`"
        )
        sys.exit(0)

    askanna_yml = scan_config_in_path()
    project_folder = os.path.dirname(askanna_yml)

    # First check whether we have a result defined
    paths = config[job_name].get("output", {}).get("result")
    if not paths:
        click.echo(
            "No output was defined in `output/result`, not pushing output to AskAnna"
        )
        sys.exit(0)

    jobresult_archive = create_jobresult(jobname=job_name, cwd=project_folder)

    click.echo("Uploading result to AskAnna...")

    fileinfo = {
        "filename": os.path.basename(jobresult_archive),
        "size": os.stat(jobresult_archive).st_size,
    }
    uploader = ResultUpload(
        api_server=api_server,
        RUN_SUUID=run_suuid,
        RESULT_SUUID=result_suuid,
    )
    status, msg = uploader.upload(jobresult_archive, config, fileinfo)
    if status:
        click.echo(msg)
        sys.exit(0)
    else:
        click.echo(msg, err=True)
        sys.exit(1)
