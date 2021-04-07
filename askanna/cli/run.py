# -*- coding: utf-8 -*-
import json
import sys

import click

from askanna import run as askanna_run
from askanna import job as askanna_job
from askanna.core.dataclasses import Project
from askanna.cli.utils import ask_which_job, ask_which_project, ask_which_workspace
from askanna.core.config import Config
from askanna.core.push import push
from askanna.core.utils import extract_push_target, getProjectInfo


config = Config()

HELP = """
This command will allow you to start a run in AskAnna.
"""

SHORT_HELP = "Start a run in AskAnna"


def determine_project(project_suuid: str = None, workspace_suuid: str = None) -> Project:
    if not project_suuid:
        # Use the project from the push-target if not set
        try:
            push_target = extract_push_target(config.push_target)
        except ValueError:
            # the push-target is not set, so don't bother reading it
            pass
        else:
            project_suuid = push_target.get("project_suuid")

    # Still if there is no project_suuid found, we will ask which project to use
    if project_suuid:
        project = getProjectInfo(project_suuid=project_suuid)
        click.echo(f"Selected project: {project.name}")

        return project
    else:
        if not workspace_suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to run a job?")
            workspace_suuid = workspace.short_uuid

        return ask_which_project(question="From which project do you want to run a job?",
                                 workspace_suuid=workspace_suuid)


@click.command(help=HELP, short_help=SHORT_HELP)
@click.argument("job_name", required=False)
@click.option("--id", "-i", "job_suuid", required=False, help="Job SUUID")
@click.option("--data", "-d", required=False, default=None, help="JSON data")
@click.option(
    "--data-file",
    "-D",
    "data_file",
    required=False,
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
@click.option("--message", "-m", required=False, help="Add description to the code")
@click.option("--project", "project_suuid", required=False, help="Project SUUID")
@click.option("--workspace", "workspace_suuid", required=False, help="Workspace SUUID")
def cli(
    job_name,
    job_suuid,
    data,
    data_file,
    project_suuid,
    workspace_suuid,
    push_code=False,
    message=None,
):
    if push_code:
        push(force=True, message=message)

    # If data and data_file is set, only use input from data
    if data:
        data = json.loads(data)
        if data_file:
            click.echo(
                "Because `--data` was set, we will not use the data from your data file"
            )
    elif data_file:
        with open(data_file) as json_file:
            data = json.load(json_file)

    # Only determine project when it's necessary
    project = None
    if not job_suuid:
        project = determine_project(project_suuid, workspace_suuid)

    if job_suuid:
        pass
    elif job_name:
        try:
            job = askanna_job.get_job_by_name(
                job_name=job_name, project_suuid=project.short_uuid
            )
            job_suuid = job.short_uuid
        except Exception as e:
            click.echo(e)
            sys.exit(1)
    else:
        job = ask_which_job(question="Which job do you want to run?", project_suuid=project.short_uuid)

        if not click.confirm(
            "\nDo you want to run the job '{}'?".format(job.name), abort=True
        ):
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
        click.echo(
            "Succesfully started a new run for job '{}' in AskAnna".format(
                run.job.get("name")
            )
        )
