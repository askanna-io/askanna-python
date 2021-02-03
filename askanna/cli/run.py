import json
import sys

import click

from askanna import run as askanna_run
from askanna import job as askanna_job
from askanna.core.config import Config
from askanna.core.dataclasses import Workspace
from askanna.core.job import Job
from askanna.core.project import Project, ProjectGateway
from askanna.core.push import push
from askanna.core.utils import extract_push_target, getProjectInfo
from askanna.core.workspace import WorkspaceGateway


config = Config()

HELP = """
This command will allow you to start a run in AskAnna.
"""

SHORT_HELP = "Start a run in AskAnna"


def ask_which_job(project: Project = None) -> Job:
    """
    Determine which job should run
    """
    job_list = askanna_job.list(project_suuid=project.short_uuid)

    job_list_str = ""
    for idx, job in enumerate(job_list, start=1):
        job_list_str += "%d. %s\n" % (idx, job.name)

    selected_job = click.prompt(
        "\nWhich job do you want to run?\n" +
        job_list_str +
        "\n" +
        "Please enter the job number",
        type=click.Choice([str(i+1) for i in range(len(job_list))]),
        show_choices=False
    )

    return job_list[int(selected_job)-1]


def ask_which_project(workspace: Workspace = None):
    """
    Determine which project to query jobs from
    """
    project_gw = ProjectGateway()
    project_list = project_gw.list(workspace=workspace)

    list_str = ""
    for idx, project in enumerate(project_list, start=1):
        list_str += "%d. %s\n" % (idx, project.name)

    selection = click.prompt(
        "\nFrom which project do you want to run a job?\n" +
        list_str +
        "\n" +
        "Please enter the project number",
        type=click.Choice([str(i+1) for i in range(len(project_list))]),
        show_choices=False
    )

    return project_list[int(selection)-1]


def determine_project(project_suuid: str = None, workspace_suuid: str = None) -> Project:
    project = None

    if not project_suuid:
        # Use the project from the push-target if not set
        try:
            push_target = extract_push_target(config.push_target)
        except ValueError as e:  # noqa
            # the push-target is not set, so don't bother reading it
            pass
        else:
            project_suuid = push_target.get('project_suuid')

    # Still if there is no project_suuid found, there we use the optional workspace
    # to preselect which workspace to select from
    if not project_suuid:
        workspace = determine_workspace(workspace_suuid)
        click.echo(f"Selected workspace: {workspace.name}")

        project = ask_which_project(workspace)

    # Set the project object
    project = project or getProjectInfo(project_suuid=project_suuid)

    return project


def determine_workspace(workspace_suuid: str = None) -> Workspace:
    workspace_gw = WorkspaceGateway()
    workspace_list = workspace_gw.list()

    if len(workspace_list) == 1 and not workspace_suuid:
        return workspace_list[0]

    list_str = ""
    for idx, workspace in enumerate(workspace_list, start=1):
        if workspace.short_uuid == workspace_suuid:
            return workspace
        list_str += "%d. %s\n" % (idx, workspace.name)

    selection = click.prompt(
        "From which workspace do you want to run a job?\n" +
        list_str +
        "\n" +
        "Please enter the workspace number",
        type=click.Choice([str(i+1) for i in range(len(workspace_list))]),
        show_choices=False
    )

    return workspace_list[int(selection)-1]


@click.command(help=HELP, short_help=SHORT_HELP)
@click.argument('job_name', required=False)
@click.option('--id', '-i', 'job_suuid', required=False, help='Job SUUID')
@click.option('--data', '-d', required=False, default=None, help='JSON data')
@click.option('--data-file', '-D', 'data_file', required=False, default=None,
              help='File with JSON data')
@click.option('--push/--no-push', '-p', 'push_code', default=False, show_default=False,
              help='Push code first, and then run the job [default: no-push]')
@click.option('--message', '-m', required=False, help='Add description to the code')
@click.option('--project', 'project_suuid', required=False, help='Project SUUID')
@click.option('--workspace', 'workspace_suuid', required=False, help='Workspace SUUID')
def cli(job_name, job_suuid, data, data_file, project_suuid, workspace_suuid, push_code=False, message=None):
    if push_code:
        push(force=True, message=message)

    # If data and data_file is set, only use input from data
    if data:
        data = json.loads(data)
        if data_file:
            click.echo("Because `--data` was set, we will not use the data from your data file")
    elif data_file:
        with open(data_file) as json_file:
            data = json.load(json_file)

    # Only determine project when it's necessary
    project = None
    if not job_suuid:
        project = determine_project(project_suuid, workspace_suuid)
        click.echo(f"Selected project: {project.name}")

    if job_suuid:
        pass
    elif job_name:
        try:
            job = askanna_job.get_job_by_name(job_name=job_name, project_suuid=project.short_uuid)
            job_suuid = job.short_uuid
        except Exception as e:
            click.echo(e)
            sys.exit(1)
    else:
        job = ask_which_job(project=project)

        if not click.confirm("\nDo you want to run the job '{}'?".format(job.name), abort=True):
            click.echo(f"Aborted! Not running job {job.name}")
        else:
            click.echo("")

        job_suuid = job.short_uuid

    try:
        run = askanna_run.start(job_suuid=job_suuid, data=data)
    except Exception as e:
        click.echo(e)
        sys.exit(1)
    else:
        click.echo("Succesfully started a new run for job '{}' in AskAnna".format(run.job.get("name")))
