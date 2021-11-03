import os
import sys
import tempfile
import uuid
from zipfile import ZipFile

import click
import git

from askanna import project as aa_project
from askanna.config import config
from askanna.core.upload import PackageUpload
from askanna.core.utils import (
    getProjectPackages,
    isIPAddress,
    validate_askanna_yml,
    zip_files_in_dir,
)


def package(src: str) -> str:

    pwd_dir_name = os.path.basename(src)
    random_suffix = uuid.uuid4().hex

    # make a temporary directory
    tmpdir = tempfile.mkdtemp(prefix="askanna-package")

    zip_file = os.path.join(
        tmpdir,
        "{pwd_dir_name}_{random_suffix}.zip".format(
            pwd_dir_name=pwd_dir_name, random_suffix=random_suffix
        ),
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


def push(force: bool, description: str = None):
    push_target = config.project.push_target.url
    if not push_target:
        click.echo(
            "`push-target` is not set, please set the `push-target` in the `askanna.yml` in order to push to "
            "AskAnna.\nMore information can be found in the documentation: https://docs.askanna.io/code/#push-target",
            err=True,
        )
        sys.exit(1)

    # read the config and parse jobs, validate the job definitions
    # then validate the job
    if not validate_askanna_yml(config.project.config_dict):
        sys.exit(1)

    # TODO: move api_server part to askanna.config.project to have it at one central location
    api_host = config.project.push_target.host
    http_scheme = config.project.push_target.http_scheme
    api_server = ''
    if api_host:
        # first also modify the first part
        if api_host.startswith("localhost") or isIPAddress(api_host.split(":")[0]):
            api_host = api_host
        elif api_host not in ["askanna.eu"]:
            # only append the -api suffix if the subdomain is not having this
            first_part = api_host.split(".")[0]
            last_part = api_host.split(".")[1:]
            if "-api" not in first_part:
                api_host = ".".join([first_part + "-api"] + last_part)
        else:
            api_host = "api." + api_host
        api_server = "{}://{}/v1/".format(http_scheme, api_host)
    project_suuid = config.project.push_target.project_suuid

    if project_suuid:
        # make an extra call to AskAnna to query for the full uuid for this project
        project_info = aa_project.detail(project_suuid)
        if project_info.short_uuid is None:
            click.echo(f"Couldn't find specified project for push target: {push_target}", err=True)
            sys.exit(1)
    else:
        click.echo("Cannot upload to AskAnna without the project SUUID set.", err=True)
        sys.exit(1)

    def ask_overwrite() -> bool:
        confirm = input("Do you want to replace the current code on AskAnna? [y/n]: ")
        answer = confirm.strip()
        if answer not in ["n", "y"]:
            print("Invalid option selected, choose from: y or n")
            return ask_overwrite()
        if confirm == "y":
            return True
        else:
            return False

    project_folder = os.path.dirname(config.project.project_config_path)

    # check for existing package
    packages = getProjectPackages(project_info)
    if packages["count"] > 0:
        # ask for confirmation if `-f` flag is not set
        overwrite = force
        if not force:
            overwrite = ask_overwrite()

        if not overwrite:
            click.echo(
                "We are not pushing your code to AskAnna. You choose not to replace your "
                "existing code.",
            )
            sys.exit(0)

    package_archive = package(project_folder)

    # attach the description to this package upload
    if not description:
        # try git
        try:
            repo = git.Repo(".")
        except Exception as e:
            click.echo(e, err=True)
        else:
            commit = repo.head.commit
            description = commit.message

    # if there is still no description set then use the zipfilename
    if not description:
        description = os.path.basename(package_archive)

    click.echo("Uploading '{}' to AskAnna...".format(project_folder))

    fileinfo = {
        "filename": os.path.basename(package_archive),
        "size": os.stat(package_archive).st_size,
    }
    uploader = PackageUpload(
        api_server=api_server,
        project_suuid=project_suuid,
        description=description,
    )
    status, msg = uploader.upload(package_archive, config, fileinfo)
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
        click.echo(msg, err=True)
        sys.exit(1)
