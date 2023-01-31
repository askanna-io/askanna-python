import os
import sys

import click

from askanna.cli.run_utils.utils import string_expand_variables
from askanna.config import config
from askanna.core.upload import ResultUpload

HELP = """
At the end of a run push the result to AskAnna
"""

SHORT_HELP = "Push result to AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option(
    "--run",
    "run_suuid",
    required=True,
    envvar="AA_RUN_SUUID",
    help="The run SUUID",
)
@click.option(
    "--job-name",
    "job_name",
    required=True,
    envvar="AA_JOB_NAME",
    help="The name of the job",
)
def cli(run_suuid, job_name):
    project_config = config.project.config_dict

    # First check whether we need to create result or not.
    # If output.result is not specified, we skip this step and report this to the stdout.
    result_path = project_config[job_name].get("output", {}).get("result")

    if not result_path:
        click.echo("  Result: no `result` defined for this job in `askanna.yml`")
        sys.exit(0)
    elif isinstance(result_path, list):
        click.echo("  Please enter a path in `result` definition, not a list.", err=True)
        sys.exit(1)

    # Expand and translate result_path if they are configured with variables
    result_path = string_expand_variables([result_path])[0]

    if not os.path.exists(result_path):
        click.echo(f"  Result: {result_path} does not exist. Not saving result.", err=True)
        sys.exit(1)

    click.echo("  Uploading result to AskAnna...")

    try:
        uploader = ResultUpload(run_suuid)
        status, msg = uploader.upload(result_path)
    except Exception as e:
        click.echo(f"  {e}", err=True)
        sys.exit(1)

    if status:
        click.echo(f"  {msg}")
        sys.exit(0)
    else:
        click.echo(f"  {msg}", err=True)
        sys.exit(1)
