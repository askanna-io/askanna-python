import json
import sys
from typing import Optional

import click

from askanna import job as aa_job
from askanna import project as aa_project
from askanna import run as aa_run
from askanna.cli.utils import ask_which_job, ask_which_project, ask_which_workspace
from askanna.config import config
from askanna.core.dataclasses.project import Project
from askanna.core.push import push

HELP = """
This command will allow you to start a run in AskAnna.
"""

SHORT_HELP = "Start a run in AskAnna"


def determine_project(
    project_suuid: Optional[str] = None,
    workspace_suuid: Optional[str] = None,
) -> Project:
    if not project_suuid:
        project_suuid = config.project.project_suuid

    # Still if there is no project_suuid found, we will ask which project to use
    if project_suuid:
        project = aa_project.get(project_suuid=project_suuid)
        click.echo(f"Selected project: {project.name}")
        return project
    else:
        if not workspace_suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to run a job?")
            workspace_suuid = workspace.suuid

        return ask_which_project(
            question="From which project do you want to run a job?",
            workspace_suuid=workspace_suuid,
        )


class SkipArgForSubCommand(click.Group):
    def parse_args(self, ctx, args):
        if args and args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                args.insert(0, "")
        super().parse_args(ctx, args)


@click.group(help=HELP, short_help=SHORT_HELP, invoke_without_command=True, cls=SkipArgForSubCommand)
@click.argument("job_name", required=False, type=str)
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
@click.option("--project", "project_suuid", required=False, type=str, help="Project SUUID")
@click.option("--workspace", "workspace_suuid", required=False, type=str, help="Workspace SUUID")
@click.pass_context
def cli(
    ctx,
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
    if ctx.invoked_subcommand is None:
        if len(description) > 0 and len(message) > 0:
            click.echo("Warning: usage of --message is deprecated. Please use --description.")
            click.echo("Cannot use both --description and --message.", err=True)
            sys.exit(1)
        elif len(message) > 0:
            click.echo("Warning: usage of --message is deprecated. Please use --description.")
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
            push(overwrite=True, description=description)

        # Only determine project when it's necessary
        project_suuid = None
        if not job_suuid:
            project = determine_project(project_suuid, workspace_suuid)
            project_suuid = project.suuid

        if job_suuid:
            pass
        elif job_name:
            job_name = job_name.strip()
            try:
                job = aa_job.get_job_by_name(job_name=job_name, project_suuid=project_suuid)
                job_suuid = job.suuid
            except Exception as e:
                click.echo(e)
                sys.exit(1)
        else:
            job = ask_which_job(
                question="Which job do you want to run?",
                project_suuid=project_suuid,
            )

            if not click.confirm(f"\nDo you want to run the job '{job.name}'?", abort=True):
                click.echo(f"Aborted! Not running job {job.name}")
            else:
                click.echo("")

            job_suuid = job.suuid

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
                f"Succesfully started a new run for job '{run.job.name}' in AskAnna with SUUID " f"'{run.suuid}'."
            )


@cli.command(help="Get the status of a run", short_help="Get run status")
@click.option("--id", "-i", "run_suuid", required=False, type=str, help="Run SUUID")
def status(run_suuid):
    run_status = aa_run.status(run_suuid=run_suuid)
    click.echo(f"Status run SUUID '{run_suuid}': {run_status.status}")


@cli.command(help="Get the log of a run", short_help="Get run log")
@click.option("--id", "-i", "run_suuid", required=False, type=str, help="Run SUUID")
def log(run_suuid):
    run_log = aa_run.log(run_suuid=run_suuid)
    click.echo(f"Log run SUUID '{run_suuid}':\n")
    for line in run_log:
        click.echo(line[2])
