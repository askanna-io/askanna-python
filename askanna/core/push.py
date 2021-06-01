import os
import sys
import tempfile
import uuid
from zipfile import ZipFile

import click
import git

from askanna.core.utils import validate_yml_job_names, validate_yml_schedule
from askanna.core.utils import zip_files_in_dir, scan_config_in_path
from askanna.core.utils import get_config, getProjectInfo, getProjectPackages
from askanna.core.utils import extract_push_target, isIPAddress, getLocalTimezone
from askanna.core.upload import PackageUpload


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

    cwd = os.getcwd()
    os.chdir(src)
    with ZipFile(zip_file, mode="w") as f:
        zip_files_in_dir(".", f)
    os.chdir(cwd)

    return zip_file


def push(force: bool, description: str = None):
    config = get_config()
    api_server = config["askanna"]["remote"]

    # read and parse the push-target from askanna
    push_target = config.get("push-target")

    if not push_target:
        click.echo(
            "`push-target` is not set, please set the `push-target` in order to push to AskAnna",
            err=True,
        )
        sys.exit(1)

    # read the config and parse jobs, validate the job definitions
    # first validate jobs names
    if not validate_yml_job_names(config):
        sys.exit(1)
    # then validate whether we have a schedule defined and validate schedule if needed
    if not validate_yml_schedule(config):
        sys.exit(1)

    # timezone set
    timezone_defined = config.get("timezone")
    timezone_local = getLocalTimezone()
    if not timezone_defined and timezone_local != "UTC":
        click.echo(  # noqa
            f"""
By default, the AskAnna platform uses time zone UTC. Your current time zone is {timezone_local}.
To use your local time zone for runnings jobs in this project, add the next line to your config in `askanna.yml`:

timezone: {timezone_local}

For more information check the documentation: https://docs.askanna.io/jobs/create-job/#time-zone
"""
        )

    matches_dict = extract_push_target(push_target)
    api_host = matches_dict.get("askanna_host")
    http_scheme = matches_dict.get("http_scheme")
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
    project_suuid = matches_dict.get("project_suuid")

    if project_suuid:
        # make an extra call to AskAnna to query for the full uuid for this project
        project_info = getProjectInfo(project_suuid)
        if project_info.uuid is None:
            click.echo(f"Couldn't find specified project {push_target}", err=True)
            sys.exit(1)

    if not project_suuid:
        click.echo("Cannot upload to AskAnna without the project SUUID set", err=True)
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

    cwd = os.getcwd()

    upload_folder = cwd
    askanna_config = scan_config_in_path()
    project_folder = os.path.dirname(askanna_config)

    def ask_which_folder(cwd, project_folder) -> str:
        confirm = input("Proceed upload [c]urrent or [p]roject folder? : ")
        answer = confirm.strip()
        if answer not in ["c", "p"]:
            print("Invalid option selected, choose from: c or p")
            return ask_which_folder(cwd, project_folder)
        if confirm == "c":
            return cwd
        if confirm == "p":
            return project_folder

    if not cwd == project_folder:
        click.echo(f"You are not at the root folder of the project '{project_folder}'.")
        upload_folder = ask_which_folder(cwd, project_folder)

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
                err=True,
            )
            sys.exit(0)

    package_archive = package(upload_folder)

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

    click.echo("Uploading '{}' to AskAnna...".format(upload_folder))

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
