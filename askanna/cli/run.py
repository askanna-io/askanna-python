import sys

import click

from askanna.cli.utils import (
    ask_which_job,
    ask_which_project,
    ask_which_run,
    ask_which_workspace,
    job_run_request,
)
from askanna.config import config
from askanna.config.utils import string_format_datetime
from askanna.core.exceptions import GetError, PatchError
from askanna.sdk.run import RunSDK

HELP = """
This command will allow you to start a run in AskAnna.
"""

SHORT_HELP = "Start a run in AskAnna"


class SkipArgForSubCommand(click.Group):
    def parse_args(self, ctx, args):
        if args and args[0] in self.commands:
            if len(args) == 1 or args[1] not in self.commands:
                args.insert(0, "")
        super().parse_args(ctx, args)


@click.group(help=HELP, short_help=SHORT_HELP, invoke_without_command=True, cls=SkipArgForSubCommand)
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
    data,
    data_file,
    push_code,
    project_suuid,
    workspace_suuid,
):
    if ctx.invoked_subcommand is None:
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


@cli.command(help="List runs available in AskAnna", short_help="List runs")
@click.option(
    "--job",
    "-j",
    "job_suuid",
    required=False,
    type=str,
    help="Job SUUID to list runs for a job",
)
@click.option(
    "--project",
    "-p",
    "project_suuid",
    required=False,
    type=str,
    help="Project SUUID to list runs for a project",
)
@click.option(
    "--workspace",
    "-w",
    "workspace_suuid",
    required=False,
    type=str,
    help="Workspace SUUID to list runs for a workspace",
)
@click.option("--search", "-s", required=False, type=str, help="Search for a specific run")
def list(job_suuid, project_suuid, workspace_suuid, search):
    run_sdk = RunSDK()
    try:
        runs = run_sdk.list(
            number_of_results=100,
            job_suuid=job_suuid,
            project_suuid=project_suuid,
            workspace_suuid=workspace_suuid,
            search=search,
            order_by="job.name,name",
        )
    except Exception as e:
        click.echo(f"Something went wrong while listing the runs:\n  {e}", err=True)
        sys.exit(1)

    if not runs:
        click.echo("We cannot find any run.")
        sys.exit(0)

    if job_suuid:
        click.echo(f"The runs for job '{runs[0].job.name}' are:\n")
        click.echo("")
        click.echo("-------------------    -------------------------")
        click.echo("RUN SUUID              RUN NAME")
        click.echo("-------------------    -------------------------")
    if not job_suuid and project_suuid:
        click.echo(f"The runs for project '{runs[0].project.name}' are:")
    if not job_suuid and not project_suuid and workspace_suuid:
        click.echo(f"The runs for workspace '{runs[0].workspace.name}' are:")
    if not job_suuid:
        click.echo("")
        click.echo("-------------------    --------------------    -------------------    -------------------------")
        click.echo("JOB SUUID              JOB NAME                RUN SUUID              RUN NAME")
        click.echo("-------------------    --------------------    -------------------    -------------------------")

    for run in runs:
        run_name = f"{run.name[:22]}..." if len(run.name) > 25 else run.name[:25]
        if job_suuid:
            click.echo(f"{run.suuid}    {run_name}")
        else:
            job_name = f"{run.job.name[:17]}..." if len(run.job.name) > 20 else run.job.name[:20]
            click.echo(
                "{job_suuid}    {job_name}    {run_suuid}    {run_name}".format(
                    job_suuid=run.job.suuid,
                    job_name=f"{job_name:20}",
                    run_suuid=run.suuid,
                    run_name=run_name,
                )
            )

    if len(runs) != run_sdk.list_total_count:
        click.echo("")
        click.echo(f"Note: the first {len(runs):,} of {run_sdk.list_total_count:,} runs are shown.")

    click.echo("")


@cli.command(help="Get information about a run", short_help="Get run info")
@click.option("--id", "-i", "run_suuid", required=False, type=str, help="Run SUUID")
def info(run_suuid):
    if run_suuid:
        try:
            run = RunSDK().get(run_suuid=run_suuid)
        except GetError as e:
            if str(e).startswith("404"):
                click.echo(f"The run SUUID '{run_suuid}' was not found", err=True)
                sys.exit(1)
            else:
                click.echo(f"Something went wrong while getting info of run SUUID '{run_suuid}':\n  {e}", err=True)
                sys.exit(1)
    else:
        project_suuid = config.project.project_suuid
        if not project_suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to get a run?")
            project = ask_which_project(
                question="From which project do you want to get a run?", workspace_suuid=workspace.suuid
            )
            project_suuid = project.suuid

        job = ask_which_job(question="From which job do you want to get a run?", project_suuid=project_suuid)
        run = ask_which_run(question="Which run do you want to get?", job_suuid=job.suuid)

    if run.metrics_meta.get("count", 0) > 0:
        metric_string = f"{run.metrics_meta.get('count')} metric" + (
            "s" if run.metrics_meta.get("count", 0) > 1 else ""
        )
    else:
        metric_string = "No metrics"

    if run.variables_meta.get("count", 0) > 0:
        variable_string = f"{run.variables_meta.get('count')} variable" + (
            "s" if run.variables_meta.get("count", 0) > 1 else ""
        )
    else:
        variable_string = "No variables"

    print_list = [
        ("Name", run.name),
        ("SUUID", run.suuid),
        ("Description", run.description),
        ("Created by", run.created_by.name),
        None,
        ("Status", run.status),
        ("Duration", f"{run.duration} seconds"),
        ("Started", run.started.strftime(string_format_datetime) if run.started else "Not started yet"),
        ("Finished", run.finished.strftime(string_format_datetime) if run.finished else "Not finished yet"),
        None,
        ("Metrics", metric_string),
        ("Variables", variable_string),
        ("Payload", "Yes" if run.payload else "No"),
        ("Result", "Yes" if run.result else "No"),
        ("Artifact", "Yes" if run.artifact else "No"),
        None,
        ("Job", run.job.name),
        ("Job SUUID", run.job.suuid),
        ("Project", run.project.name),
        ("Project SUUID", run.project.suuid),
        ("Workspace", run.workspace.name),
        ("Workspace SUUID", run.workspace.suuid),
        None,
        ("Created", run.created.strftime(string_format_datetime)),
        ("Modified", run.modified.strftime(string_format_datetime)),
        None,
    ]
    for item in print_list:
        if item is None:
            click.echo("")
        else:
            click.echo(f"{item[0] + ':':16} {item[1]}")


@cli.command(help="Get the status of a run", short_help="Get run status")
@click.option("--id", "-i", "run_suuid", required=False, type=str, help="Run SUUID")
def status(run_suuid):
    run_status = RunSDK().status(run_suuid=run_suuid)
    click.echo(f"Status run SUUID '{run_suuid}': {run_status.status}")


@cli.command(help="Get the log of a run", short_help="Get run log")
@click.option("--id", "-i", "run_suuid", required=False, type=str, help="Run SUUID")
def log(run_suuid):
    run_log = RunSDK().log(run_suuid=run_suuid)
    click.echo(f"Log run SUUID '{run_suuid}':\n")
    for line in run_log:
        click.echo(line[2])


@cli.command(help="Change run information in AskAnna", short_help="Change run")
@click.option("--id", "-i", "run_suuid", required=False, type=str, help="Run SUUID")
@click.option("--name", "-n", required=False, type=str, help="New name to set")
@click.option("--description", "-d", required=False, type=str, help="New description to set")
def change(run_suuid, name, description):
    if not run_suuid:
        project_suuid = config.project.project_suuid
        if not project_suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to change a run?")
            project = ask_which_project(
                question="From which project do you want to change a run?", workspace_suuid=workspace.suuid
            )
            project_suuid = project.suuid

        job = ask_which_job(question="From which job do you want to change a run?", project_suuid=project_suuid)
        run = ask_which_run(question="Which run do you want to change?", job_suuid=job.suuid)
        run_suuid = run.suuid

    if not name and not description:
        if click.confirm("\nDo you want to change the name of the run?"):
            name = click.prompt("New name of the run", type=str)
        if click.confirm("\nDo you want to change the description of the run?"):
            description = click.prompt("New description of the run", type=str)

        click.confirm("\nDo you want to change the run?", abort=True)

    try:
        run = RunSDK().change(run_suuid=run_suuid, name=name, description=description)
    except PatchError as e:
        if str(e).startswith("404"):
            click.echo(f"The run SUUID '{run_suuid}' was not found", err=True)
        else:
            click.echo(f"Something went wrong while changing the run SUUID '{run_suuid}':\n  {e}", err=True)
        sys.exit(1)

    click.echo(f"\nYou succesfully changed run '{run.name}' with SUUID '{run.suuid}'")


@cli.command(help="Remove a run in AskAnna", short_help="Remove run")
@click.option("--id", "-i", "run_suuid", type=str, required=False, help="Run SUUID")
@click.option("--force", "-f", is_flag=True, help="Force")
def remove(run_suuid, force):
    if run_suuid:
        try:
            run = RunSDK().get(run_suuid=run_suuid)
        except GetError as e:
            if str(e).startswith("404"):
                click.echo(f"The run SUUID '{run_suuid}' was not found", err=True)
            else:
                click.echo(f"Something went wrong while getting the info of run SUUID '{run_suuid}':\n  {e}", err=True)
            sys.exit(1)

    else:
        project_suuid = config.project.project_suuid
        if not project_suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to remove a run?")
            project = ask_which_project(
                question="From which project do you want to remove a run?", workspace_suuid=workspace.suuid
            )
            project_suuid = project.suuid

        job = ask_which_job(question="From which job do you want to remove a run?", project_suuid=project_suuid)
        run = ask_which_run(question="Which run do you want to remove?", job_suuid=job.suuid)

    if not force:
        if not click.confirm(f"Are you sure to remove run SUUID '{run.suuid}'?"):
            click.echo("Understood. We are not removing the run.")
            sys.exit(0)

    try:
        _ = RunSDK().delete(run_suuid=run.suuid)
    except Exception as e:
        click.echo(f"Something went wrong while removing the run SUUID '{run.suuid}':\n  {e}", err=True)
        sys.exit(1)

    click.echo(f"You removed run SUUID '{run.suuid}'")
