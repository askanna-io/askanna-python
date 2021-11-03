# -*- coding: utf-8 -*-
import json
import sys

import click

from askanna import (
    job as aa_job,
    project as aa_project,
    run as aa_run,
)
from askanna.config import config
from askanna.core.dataclasses import Project
from askanna.cli.utils import ask_which_job, ask_which_project, ask_which_workspace
from askanna.core.push import push


HELP = """
This command will allow you to start a run in AskAnna.
"""

SHORT_HELP = "Start a run in AskAnna"


def determine_project(
    project_suuid: str = None,
    workspace_suuid: str = None,
) -> Project:
    if not project_suuid:
        project_suuid = config.project.project_suuid

    # Still if there is no project_suuid found, we will ask which project to use
    if project_suuid:
        project = aa_project.detail(project_suuid)
        click.echo(f"Selected project: {project.name}")
        return project
    else:
        if not workspace_suuid:
            workspace = ask_which_workspace(
                question="From which workspace do you want to run a job?"
            )
            workspace_suuid = workspace.short_uuid

        return ask_which_project(
            question="From which project do you want to run a job?",
            workspace_suuid=workspace_suuid,
        )


@click.command(help=HELP, short_help=SHORT_HELP)
@click.argument(
    "job_name",
    required=False,
    type=str,
)
@click.option("--id", "-i", "job_suuid", required=False, type=str, help="Job SUUID")
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
    show_default=False,
    help="Push code first, and then run the job [default: no-push]",
)
@click.option("--name", "-n", required=False, type=str, help="Give the run a name")
@click.option(
    "--description",
    required=False,
    type=str,
    help="Description of the run",
    default="",
)
@click.option(
    "--message",
    "-m",
    required=False,
    type=str,
    help="[deprecated] Description of the run",
    default="",
)
@click.option(
    "--project", "project_suuid", required=False, type=str, help="Project SUUID"
)
@click.option(
    "--workspace", "workspace_suuid", required=False, type=str, help="Workspace SUUID"
)
def cli(
    job_name,
    job_suuid,
    name,
    description,
    message,
    data,
    data_file,
    project_suuid,
    workspace_suuid,
    push_code,
):
    if len(description) > 0 and len(message) > 0:
        click.echo(
            "Warning: usage of --message is deprecated. Please use --description."
        )
        click.echo("Cannot use both --description and --message.", err=True)
        sys.exit(1)
    elif len(message) > 0:
        click.echo(
            "Warning: usage of --message is deprecated. Please use --description."
        )
        description = message

    if data and data_file:
        click.echo("Cannot use both --data and --data-file.", err=True)
        sys.exit(1)
    elif data:
        data = json.loads(data)
    elif data_file:
        with open(data_file) as json_file:
            data = json.load(json_file)

    if push_code:
        push(force=True, description=description)

    # Only determine project when it's necessary
    project = None
    if not job_suuid:
        project = determine_project(project_suuid, workspace_suuid)

    if job_suuid:
        pass
    elif job_name:
        try:
            job = aa_job.get_job_by_name(
                job_name=job_name, project_suuid=project.short_uuid
            )
            job_suuid = job.short_uuid
        except Exception as e:
            click.echo(e)
            sys.exit(1)
    else:
        job = ask_which_job(
            question="Which job do you want to run?",
            project_suuid=project.short_uuid,
        )

        if not click.confirm(f"\nDo you want to run the job '{job.name}'?", abort=True):
            click.echo(f"Aborted! Not running job {job.name}")
        else:
            click.echo("")

        job_suuid = job.short_uuid

    try:
        run = aa_run.start(
            job_suuid=job_suuid,
            data=data,
            name=name,
            description=description,
        )
    except Exception as e:
        click.echo(e)
        sys.exit(1)
    else:
        click.echo(
            "Succesfully started a new run for job '{}' in AskAnna".format(
                run.job.get("name")
            )
        )
