# -*- coding: utf-8 -*-
import click
import sys

from askanna import job as aa_job
from askanna import project as aa_project
from askanna.cli.utils import ask_which_job, ask_which_project, ask_which_workspace
from askanna.config import config


@click.group()
def cli1():
    pass


@cli1.command(help="List jobs available in AskAnna",
              short_help="List jobs")
@click.option(
    "--project", "-p", "project_suuid",
    required=False,
    type=str,
    help="Project SUUID to list jobs for a project"
)
def list(project_suuid):
    jobs = aa_job.list(project_suuid)

    if not jobs:
        click.echo("Based on the information provided, we cannot find any jobs.")
        sys.exit(0)
    elif project_suuid:
        project = aa_project.detail(project_suuid)
        print("The jobs for project \"{}\" are:\n".format(project.name))
        print("JOB SUUID              JOB NAME")
        print("-------------------    -------------------------")
    else:
        print("PROJECT SUUID          PROJECT NAME            JOB SUUID              JOB NAME")
        print("-------------------    --------------------    -------------------    -------------------------")

    for job in sorted(jobs, key=lambda x: (x.project["name"], x.name)):
        if project_suuid:
            print("{job_suuid}    {job_name}".format(
                  job_suuid=job.short_uuid,
                  job_name=job.name[:25]))
        else:
            print("{project_suuid}    {project_name}    {job_suuid}    {job_name}".format(
                project_suuid=job.project["short_uuid"],
                project_name="{:20}".format(job.project["name"])[:20],
                job_suuid=job.short_uuid,
                job_name=job.name[:25]))


@cli1.command(help="Change job information in AskAnna", short_help="Change job")
@click.option("--id", "-i", "suuid", required=False, type=str, help="Job SUUID")
@click.option("--name", "-n", required=False, type=str, help="New name to set")
@click.option("--description", "-d", required=False, type=str, help="New description to set")
def change(suuid, name, description):
    if not suuid:
        project_suuid = config.project.project_suuid

        if not project_suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to change a job?")
            project = ask_which_project(question="From which project do you want to change a job?",
                                        workspace_suuid=workspace.short_uuid)
            project_suuid = project.short_uuid

        job = ask_which_job(question="Which job do you want to change?", project_suuid=project_suuid)
        suuid = job.short_uuid

    if not name and not description:
        if click.confirm("\nDo you want to change the name of the job?"):
            name = click.prompt("New name of the job", type=str)
        if click.confirm("\nDo you want to change the description of the job?"):
            description = click.prompt("New description of the job", type=str)

        click.confirm("\nDo you want to change the job?", abort=True)

    aa_job.change(suuid=suuid, name=name, description=description)


cli = click.CommandCollection(
    sources=[cli1],
    help="Manage your jobs in AskAnna",
    short_help="Manage jobs in AskAnna",
)
