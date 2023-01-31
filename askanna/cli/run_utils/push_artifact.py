import os
import sys
import tempfile

import click

from askanna.cli.run_utils.utils import string_expand_variables
from askanna.config import config
from askanna.core.upload import ArtifactUpload
from askanna.core.utils.file import create_zip_from_paths

HELP = """
Push the artifact of a run to AskAnna
"""

SHORT_HELP = "Push artifact to AskAnna"


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

    # First check whether we need to create an artifact or not.
    # If output.artifact or output.paths is not specified, we skip this step and report this to the stdout.
    paths_defined = project_config[job_name].get("output", {}).get("artifact", [])

    if not paths_defined:
        click.echo("  Artifact: no `artifact` defined for this job in `askanna.yml`")
        sys.exit(0)
    elif isinstance(paths_defined, str):
        paths_defined = [paths_defined]

    # Expand and translate paths if they are configured with variables
    paths = string_expand_variables(paths_defined)

    click.echo("  Making a zip file with artifact...")

    tempdir = tempfile.mkdtemp(prefix="askanna-artifact")
    zip_file = os.path.join(tempdir, f"artifact_{run_suuid}.zip")
    create_zip_from_paths(filename=zip_file, paths=paths)

    click.echo("  Uploading artifact to AskAnna...")

    try:
        uploader = ArtifactUpload(run_suuid)
        status, msg = uploader.upload(zip_file)
    except Exception as e:
        click.echo(f"  {e}", err=True)
        sys.exit(1)

    if status:
        click.echo(f"  {msg}")
        try:
            os.remove(zip_file)
            os.rmdir(tempdir)
        except OSError as e:
            click.echo("  Pushing the artifact was successful, but the temporary file could not be removed.", err=True)
            click.echo(f"  The error: {e.strerror}", err=True)
            click.echo(f"  You can manually delete the file: {zip_file}", err=True)
        sys.exit(0)
    else:
        click.echo(f"  {msg}", err=True)
        sys.exit(1)
