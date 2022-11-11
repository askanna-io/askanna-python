import sys

import click

from askanna import job as aa_job
from askanna.cli.utils import ask_which_job, ask_which_project, ask_which_workspace
from askanna.config import config
from askanna.core.exceptions import GetError, PatchError


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
def list(project_suuid):
    try:
        jobs = aa_job.list(project_suuid=project_suuid)
    except Exception as e:
        click.echo(f"Something went wrong while listing the jobs:\n  {e}", err=True)
        sys.exit(1)

    if not jobs:
        click.echo("We cannot find any job.")
    if project_suuid:
        click.echo(f"The jobs for project '{jobs[0].project.name}' are:\n")
        click.echo("JOB SUUID              JOB NAME")
        click.echo("-------------------    -------------------------")
    else:
        click.echo("PROJECT SUUID          PROJECT NAME            JOB SUUID              JOB NAME")
        click.echo("-------------------    --------------------    -------------------    -------------------------")

    for job in sorted(jobs, key=lambda x: (x.project.name, x.name)):
        if project_suuid:
            click.echo(f"{job.suuid}    {job.name[:25]}")
        else:
            click.echo(
                "{project_suuid}    {project_name}    {job_suuid}    {job_name}".format(
                    project_suuid=job.project.suuid,
                    project_name=f"{job.project.name:20}"[:20],
                    job_suuid=job.suuid,
                    job_name=job.name[:25],
                )
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
        job = aa_job.change(job_suuid=job_suuid, name=name, description=description)
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
        job = aa_job.detail(job_suuid=job_suuid)
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
        removed = aa_job.delete(job_suuid=job_suuid)
    except Exception as e:
        click.echo(f"Something went wrong while removing the job SUUID '{job_suuid}':\n  {e}", err=True)
        sys.exit(1)
    else:
        if removed:
            click.echo(f"You removed job SUUID '{job_suuid}'")
        else:
            click.echo(f"Something went wrong. Removing the job SUUID '{job_suuid}' aborted.", err=True)
            sys.exit(1)


cli = click.CommandCollection(
    sources=[cli1],
    help="Manage your jobs in AskAnna",
    short_help="Manage jobs in AskAnna",
)
