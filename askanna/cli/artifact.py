# -*- coding: utf-8 -*-
import os
import sys
from zipfile import ZipFile
import click

from askanna.core.download import ChunkedDownload
from askanna.core.utils import zipPaths
from askanna.core.utils import scan_config_in_path
from askanna.core.utils import get_config, string_expand_variables
from askanna.core.upload import ArtifactUpload


@click.group()
def cli1():
    pass


@click.group()
def cli2():
    pass


def create_artifact(cwd: str, paths: list) -> str:
    # expand and translate paths if they are configured with variables
    paths = string_expand_variables(paths)

    zipFileName = "/tmp/artifact.zip"
    with ZipFile(zipFileName, mode="w") as zipObj:
        zipPaths(zipObj, paths, cwd)

    return zipFileName


@cli1.command(
    help="After a run, save the artifact", short_help="Save artifact from a run"
)
def add():
    config = get_config()
    api_server = config["askanna"]["remote"]

    project_suuid = os.getenv("AA_PROJECT_SUUID")
    run_suuid = os.getenv("AA_RUN_SUUID")
    job_name = os.getenv("AA_JOB_NAME")

    if not project_suuid:
        click.echo("Cannot upload from unregistered project to AskAnna", err=True)
        sys.exit(1)

    # first check whether we need to create artifacts or not
    # if output.artifact or output.paths is not specified
    # then we skip this step and report this to the stdout
    paths_defined = config[job_name].get("output", {}).get("paths", [])
    paths_defined = paths_defined + config[job_name].get("output", {}).get(
        "artifact", []
    )

    if not paths_defined:
        click.echo(
            "Artifact creation aborted, no `output/artifact` or `output/paths` defined for "
            "this job in `askanna.yml`"
        )
        sys.exit(0)

    cwd = os.getcwd()

    upload_folder = cwd
    askanna_config = scan_config_in_path()
    project_folder = os.path.dirname(askanna_config)

    def ask_which_folder(cwd, project_folder) -> str:
        confirm = input("Proceed upload [c]urrent or [p]roject folder? : ")
        answer = confirm.strip()
        if answer not in ["c", "p"]:
            return ask_which_folder(cwd, project_folder)
        if confirm == "c":
            return cwd
        if confirm == "p":
            return project_folder

    if not cwd == project_folder:
        click.echo(
            "You are not at the root folder of the project '{}'.".format(project_folder)
        )
        upload_folder = ask_which_folder(cwd, project_folder)

    artifact_archive = create_artifact(cwd=upload_folder, paths=paths_defined)

    click.echo("Uploading artifact to AskAnna...")

    fileinfo = {
        "filename": os.path.basename(artifact_archive),
        "size": os.stat(artifact_archive).st_size,
    }
    uploader = ArtifactUpload(
        api_server=api_server,
        PROJECT_SUUID=project_suuid,
        RUN_SUUID=run_suuid,
    )
    status, msg = uploader.upload(artifact_archive, config, fileinfo)
    if status:
        click.echo(msg)
        sys.exit(0)
    else:
        click.echo(msg)
        sys.exit(1)


@cli2.command(
    help="Download an artifact of a run", short_help="Download a run artifact"
)
@click.option("--id", "-i", "suuid", prompt='Run SUUID', required=True, type=str, help="Run SUUID")
@click.option("--output", "-o", "output_path", show_default=True, type=click.Path(), help="File name to save (zip)")
def get(suuid, output_path):
    """
    Download an artifact of a run
    """
    config = get_config()
    ASKANNA_API_SERVER = config.get("askanna", {}).get("remote")
    url = f"{ASKANNA_API_SERVER}artifact/{suuid}/"

    if not output_path:
        output_path = f"artifact_{suuid}.zip"

    if os.path.isdir(output_path):
        click.echo(
            "The output argument is a directory. Please provide a file name (zip) for the output.",
            err=True
        )
        sys.exit(1)

    if os.path.exists(output_path):
        click.echo(
            "The output file already exists. We will not overwrite the existing file.",
            err=True,
        )
        sys.exit(1)

    stable_download = ChunkedDownload(url=url)
    if stable_download.status_code != 200:
        click.echo("We cannot find this artifact for you.", err=True)
        sys.exit(1)
    click.echo("Downloading the artifact has started...")
    stable_download.download(output_file=output_path)
    click.echo("We have succesfully downloaded the artifact.")
    click.echo(f"The artifact is saved in: {output_path}")


cli = click.CommandCollection(
    sources=[cli1, cli2],
    help="Download artifact of a run",
    short_help="Download run artifact",
)
