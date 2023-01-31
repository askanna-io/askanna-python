import sys

import click

from askanna.cli.utils import (
    ask_which_job,
    ask_which_project,
    ask_which_workspace,
    job_run_request,
)
from askanna.config import config
from askanna.core.exceptions import GetError, PatchError
from askanna.sdk.job import JobSDK


@click.group()
def cli1():
    pass


@cli1.command(help="List jobs available in AskAnna", short_help="List jobs")
@click.option(
    "--project",
    "-p",
    "project_suuid",
    required=False,
    type=str,
    help="Project SUUID to list jobs for a project",
)
@click.option(
    "--workspace",
    "-w",
    "workspace_suuid",
    required=False,
    type=str,
    help="Workspace SUUID to list jobs for a workspace",
)
@click.option("--search", "-s", required=False, type=str, help="Search for a specific job")
def list(project_suuid, workspace_suuid, search):
    job_sdk = JobSDK()
    try:
        jobs = job_sdk.list(
            number_of_results=100,
            project_suuid=project_suuid,
            workspace_suuid=workspace_suuid,
            search=search,
            order_by="project.name,name",
        )
    except Exception as e:
        click.echo(f"Something went wrong while listing the jobs:\n  {e}", err=True)
        sys.exit(1)

    if not jobs:
        click.echo("We cannot find any job.")
        sys.exit(0)

    if project_suuid:
        click.echo(f"The jobs for project '{jobs[0].project.name}' are:\n")
        click.echo("")
        click.echo("-------------------    -------------------------")
        click.echo("JOB SUUID              JOB NAME")
        click.echo("-------------------    -------------------------")
    if not project_suuid and workspace_suuid:
        click.echo(f"The jobs for workspace '{jobs[0].workspace.name}' are:")
    if not project_suuid:
        click.echo("")
        click.echo("-------------------    --------------------    -------------------    -------------------------")
        click.echo("PROJECT SUUID          PROJECT NAME            JOB SUUID              JOB NAME")
        click.echo("-------------------    --------------------    -------------------    -------------------------")

    for job in jobs:
        job_name = f"{job.name[:22]}..." if len(job.name) > 25 else job.name[:25]
        if project_suuid:
            click.echo(f"{job.suuid}    {job_name}")
        else:
            project_name = f"{job.project.name[:17]}..." if len(job.project.name) > 20 else job.project.name[:20]
            click.echo(
                "{project_suuid}    {project_name}    {job_suuid}    {job_name}".format(
                    project_suuid=job.project.suuid,
                    project_name=f"{project_name:20}",
                    job_suuid=job.suuid,
                    job_name=job_name,
                )
            )

    if len(jobs) != job_sdk.list_total_count:
        click.echo("")
        click.echo(f"Note: the first {len(jobs):,} of {job_sdk.list_total_count:,} jobs are shown.")

    click.echo("")


@cli1.command(help="Get information about a job", short_help="Get job info")
@click.option("--id", "-i", "job_suuid", required=False, type=str, help="Job SUUID")
def info(job_suuid):
    if job_suuid:
        try:
            job = JobSDK().get(job_suuid=job_suuid)
        except Exception as e:
            click.echo(f"Something went wrong while getting the job info:\n  {e}", err=True)
            sys.exit(1)
    else:
        project_suuid = config.project.project_suuid
        if not project_suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to get a job?")
            project = ask_which_project(
                question="From which project do you want to get a job?", workspace_suuid=workspace.suuid
            )
            project_suuid = project.suuid

        job = ask_which_job(question="Which job do you want to get?", project_suuid=project_suuid)

    scheduled = "Yes" if job.schedules else "No"
    notifications = "No"
    if job.notifications and (
        job.notifications.get("all", {}).get("email") or job.notifications.get("error", {}).get("email")
    ):
        notifications = "Yes"

    click.echo("")
    click.echo(f"Name:        {job.name}")
    click.echo(f"SUUID:       {job.suuid}")
    click.echo(f"Description: {job.description}")
    click.echo("")
    click.echo(f"Environment:   {job.environment}")
    click.echo(f"Timezone:      {job.timezone}")
    click.echo(f"Scheduled:     {scheduled}")
    click.echo(f"Notifications: {notifications}")
    click.echo("")
    click.echo(f"Project:         {job.project.name}")
    click.echo(f"Project SUUID:   {job.project.suuid}")
    click.echo(f"Workspace:       {job.workspace.name}")
    click.echo(f"Workspace SUUID: {job.workspace.suuid}")
    click.echo("")
    click.echo(f"Created:  {job.created}")
    click.echo(f"Modified: {job.modified}")
    click.echo("")


@cli1.command(help="Do a request to run a job on the AskAnna platform", short_help="Request to run a job")
@click.argument("job_name", required=False, type=str)
@click.option("--id", "-i", "job_suuid", required=False, type=str, help="SUUID of the job to run")
@click.option("--data", "-d", required=False, type=str, default=None, help="JSON data")
@click.option(
    "--data-file",
    "-D",
    "data_file",
    required=False,
    type=str,
    default=None,
    help="File with JSON data",
)
@click.option(
    "--push/--no-push",
    "-p",
    "push_code",
    default=False,
    show_default=True,
    help="Push code before starting a run",
)
@click.option("--name", "-n", required=False, type=str, help="Give the run a name")
@click.option(
    "--description",
    required=False,
    type=str,
    help="Description of the run",
    default=None,
)
@click.option("--project", "project_suuid", required=False, type=str, help="Project SUUID")
@click.option("--workspace", "workspace_suuid", required=False, type=str, help="Workspace SUUID")
def run_request(
    job_name,
    job_suuid,
    name,
    description,
    data,
    data_file,
    push_code,
    project_suuid,
    workspace_suuid,
):
    job_run_request(
        job_name=job_name,
        job_suuid=job_suuid,
        name=name,
        description=description,
        data=data,
        data_file=data_file,
        push_code=push_code,
        project_suuid=project_suuid,
        workspace_suuid=workspace_suuid,
    )


@cli1.command(help="Change job information in AskAnna", short_help="Change job")
@click.option("--id", "-i", "job_suuid", required=False, type=str, help="Job SUUID")
@click.option("--name", "-n", required=False, type=str, help="New name to set")
@click.option("--description", "-d", required=False, type=str, help="New description to set")
def change(job_suuid, name, description):
    if not job_suuid:
        project_suuid = config.project.project_suuid

        if not project_suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to change a job?")
            project = ask_which_project(
                question="From which project do you want to change a job?", workspace_suuid=workspace.suuid
            )
            project_suuid = project.suuid

        job = ask_which_job(question="Which job do you want to change?", project_suuid=project_suuid)
        job_suuid = job.suuid

    if not name and not description:
        if click.confirm("\nDo you want to change the name of the job?"):
            name = click.prompt("New name of the job", type=str)
        if click.confirm("\nDo you want to change the description of the job?"):
            description = click.prompt("New description of the job", type=str)

        click.confirm("\nDo you want to change the job?", abort=True)

    try:
        job = JobSDK().change(job_suuid=job_suuid, name=name, description=description)
    except PatchError as e:
        if str(e).startswith("404"):
            click.echo(f"The job SUUID '{job_suuid}' was not found", err=True)
            sys.exit(1)
        else:
            click.echo(f"Something went wrong while changing the job SUUID '{job_suuid}':\n  {e}", err=True)
            sys.exit(1)
    else:
        click.echo(f"\nYou succesfully changed job '{job.name}' with SUUID '{job.suuid}'")


@cli1.command(help="Remove a job in AskAnna", short_help="Remove job")
@click.option("--id", "-i", "job_suuid", type=str, required=True, help="Job SUUID", prompt="Job SUUID")
@click.option("--force", "-f", is_flag=True, help="Force")
def remove(job_suuid, force):
    try:
        job = JobSDK().get(job_suuid=job_suuid)
    except GetError as e:
        if str(e).startswith("404"):
            click.echo(f"The job SUUID '{job_suuid}' was not found", err=True)
            sys.exit(1)
        else:
            click.echo(f"Something went wrong while removing the job SUUID '{job_suuid}':\n  {e}", err=True)
            sys.exit(1)

    if not force:
        if not click.confirm(f"Are you sure to remove job SUUID '{job_suuid}' with name '{job.name}'?"):
            click.echo("Understood. We are not removing the job.")
            sys.exit(0)

    try:
        _ = JobSDK().delete(job_suuid=job_suuid)
    except Exception as e:
        click.echo(f"Something went wrong while removing the job SUUID '{job_suuid}':\n  {e}", err=True)
        sys.exit(1)
    else:
        click.echo(f"You removed job SUUID '{job_suuid}'")


cli = click.CommandCollection(
    sources=[cli1],
    help="Manage your jobs in AskAnna",
    short_help="Manage jobs in AskAnna",
)
