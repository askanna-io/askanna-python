import os
import sys
import tempfile
import uuid
from typing import Union
from zipfile import ZipFile

import click
import git

from askanna.config import config
from askanna.core.upload import PackageUpload
from askanna.core.utils.file import zip_files_in_dir
from askanna.core.utils.validate import validate_askanna_yml
from askanna.sdk.package import PackageSDK


def package(src: str) -> str:
    pwd_dir_name = os.path.basename(src)
    random_suffix = uuid.uuid4().hex

    # make a temporary directory
    tmpdir = tempfile.mkdtemp(prefix="askanna-package")

    zip_file = os.path.join(
        tmpdir,
        f"{pwd_dir_name}_{random_suffix}.zip",
    )

    if os.path.isfile(os.path.join(src, "askannaignore")):
        ignore_file = os.path.join(src, "askannaignore")
    elif os.path.isfile(os.path.join(src, ".askannaignore")):
        ignore_file = os.path.join(src, ".askannaignore")
    elif os.path.isfile(os.path.join(src, ".gitignore")):
        ignore_file = os.path.join(src, ".gitignore")
    else:
        ignore_file = None

    cwd = os.getcwd()
    os.chdir(src)
    with ZipFile(zip_file, mode="w") as f:
        zip_files_in_dir(".", f, ignore_file)
    os.chdir(cwd)

    return zip_file


def is_project_config_push_ready() -> bool:
    if not config.project.project_config_path:
        click.echo(
            "We cannot upload without a project config path.\n\nThe project path is set by adding an `askanna.yml` "
            "file to your project root directory.\nIf you have an `askanna.yml` file, please check if your working "
            "directory is set to a project (sub)directory with the `askanna.yml` file.",
            err=True,
        )
        return False

    if not config.project.project_suuid:
        click.echo(
            "We cannot upload to AskAnna without the project SUUID set. Did you add a push-target to your "
            "`askanna.yml` file?",
            err=True,
        )
        return False

    return True


def push(overwrite: bool = False, description: Union[str, None] = None) -> bool:

    if not is_project_config_push_ready():
        sys.exit(1)

    if not validate_askanna_yml(config.project.config_dict):
        sys.exit(1)

    if not overwrite:
        # If a package for the project exists, we will not push a new version.
        packages = PackageSDK().list(project_suuid=config.project.project_suuid, number_of_results=1)
        if len(packages) > 0:
            click.echo(
                "We are not pushing your code to AskAnna because this project already has a code package and "
                "overwrite is set to `False`.",
                err=True,
            )
            sys.exit(1)

    project_folder = os.path.dirname(config.project.project_config_path)
    package_archive = package(project_folder)

    # Attach the description to this package upload
    if not description:
        # Try git and use last commit message
        try:
            repo = git.Repo(".")
        except Exception as e:
            click.echo(e, err=True)
        else:
            commit = repo.head.commit
            description = commit.message

    click.echo(f"Uploading '{project_folder}' to AskAnna...")

    uploader = PackageUpload(
        project_suuid=config.project.project_suuid,
        description=description,
    )
    status, _ = uploader.upload(package_archive)
    if status:
        # remove temporary zip-file from the system including the parent temporary folder
        try:
            os.remove(package_archive)
            os.rmdir(os.path.dirname(package_archive))
            click.echo("Successfully pushed the project to AskAnna!")
        except OSError as e:
            click.echo(
                "Pushing your code was successful, but we could not remove the temporary file "
                "used for uploading your code to AskAnna.",
                err=True,
            )
            click.echo(f"The error: {e.strerror}", err=True)
            click.echo(f"You can manually delete the file: {package_archive}", err=True)
    else:
        click.echo("Pushing your code failed.", err=True)
        sys.exit(1)

    return status
