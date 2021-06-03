# -*- coding: utf-8 -*-
import os
import sys
import click

from askanna.core.utils import get_config
from askanna.core.upload import ResultUpload

HELP = """
At the end of a run push the result to AskAnna
"""

SHORT_HELP = "Push result to AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    config = get_config()
    api_server = config["askanna"]["remote"]

    run_suuid = os.getenv("AA_RUN_SUUID")
    job_name = os.getenv("AA_JOB_NAME")

    result_suuid = os.getenv("AA_RESULT_SUUID")

    # First check whether we need to create result or not.
    # If output.result is not specified, we skip this step and report this to the stdout.

    result_path = config[job_name].get("output", {}).get("result")

    if not result_path:
        click.echo(
            "Result storage aborted. No `output/result` defined for this job in `askanna.yml`."
        )
        sys.exit(0)
    elif isinstance(result_path, list):
        click.echo("Please enter a path in `output/result`, not a list.", err=True)
        sys.exit(1)
    elif not os.path.exists(result_path):
        click.echo(
            f"output/result: {result_path} does not exist. Not saving result.", err=True
        )
        sys.exit(1)

    click.echo("Uploading result to AskAnna...")

    fileinfo = {
        "filename": os.path.basename(result_path),
        "size": os.stat(result_path).st_size,
    }
    uploader = ResultUpload(
        api_server=api_server,
        RUN_SUUID=run_suuid,
        RESULT_SUUID=result_suuid,
    )
    status, msg = uploader.upload(result_path, config, fileinfo)
    if status:
        click.echo(msg)
        sys.exit(0)
    else:
        click.echo(msg, err=True)
        sys.exit(1)
