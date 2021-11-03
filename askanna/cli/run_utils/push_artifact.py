# -*- coding: utf-8 -*-
import os
import sys
import click
import tempfile

from askanna.cli.run_utils.utils import string_expand_variables
from askanna.config import config
from askanna.core.upload import ArtifactUpload
from askanna.core.utils import create_zip_from_paths


HELP = """
Push the artifact of a run to AskAnna
"""

SHORT_HELP = "Push artifact to AskAnna"


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    project_config = config.project.config_dict
    run_suuid = os.getenv("AA_RUN_SUUID")
    job_name = os.getenv("AA_JOB_NAME")

    if not run_suuid:
        click.echo("Cannot push artifact from unregistered run to AskAnna.", err=True)
        sys.exit(1)

    if not job_name:
        click.echo(
            "The job name is not set. We cannot push artifact to AskAnna.", err=True
        )
        sys.exit(1)

    # First check whether we need to create an artifact or not.
    # If output.artifact or output.paths is not specified, we skip this step and report this to the stdout.
    paths_defined = project_config[job_name].get("output", {}).get("artifact", [])

    if not paths_defined:  # deprecated: can be removed after release of aa-core v0.5.0
        paths_defined = project_config[job_name].get("output", {}).get("paths", [])
        if paths_defined:
            click.echo(
                "Deprecation warning: in a future version we remove the output/paths option. Please specify "
                "the artifact paths you want to keep in output/artifact."
            )
            click.echo(
                "More info in the documentation: https://docs.askanna.io/jobs/create-job/"
            )

    if not paths_defined:
        click.echo(
            "Artifact creation aborted, no `output/artifact` defined for this job in `askanna.yml`"
        )
        sys.exit(0)
    elif isinstance(paths_defined, str):
        paths_defined = [paths_defined]

    # Expand and translate paths if they are configured with variables
    paths = string_expand_variables(paths_defined)

    click.echo("Making a zip file with artifact...")

    tempdir = tempfile.mkdtemp(prefix="askanna-artifact")
    zip_file = os.path.join(tempdir, f"artifact_{run_suuid}.zip")
    create_zip_from_paths(filename=zip_file, paths=paths)

    click.echo("Uploading artifact to AskAnna...")

    fileinfo = {
        "filename": os.path.basename(zip_file),
        "size": os.stat(zip_file).st_size,
    }
    uploader = ArtifactUpload(
        run_suuid=run_suuid,
    )
    status, msg = uploader.upload(zip_file, project_config, fileinfo)
    if status:
        click.echo(msg)
        try:
            os.remove(zip_file)
            os.rmdir(tempdir)
        except OSError as e:
            click.echo(
                "Pushing your artifact was successful, but we could not remove the temporary file "
                "used for uploading the artifact to AskAnna.",
                err=True,
            )
            click.echo(f"The error: {e.strerror}", err=True)
            click.echo(f"You can manually delete the file: {zip_file}", err=True)
        sys.exit(0)
    else:
        click.echo(msg, err=True)
        sys.exit(1)
