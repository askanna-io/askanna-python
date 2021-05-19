# -*- coding: utf-8 -*-
import click
import sys

from askanna import project as aa_project
from askanna.cli.utils import ask_which_project, ask_which_workspace
from askanna.core.config import Config
from askanna.core.utils import extract_push_target


config = Config()


@click.group()
def cli1():
    pass


@cli1.command(help="List projects available in AskAnna", short_help="List projects")
@click.option('--workspace', '-w', 'workspace_suuid', required=False, type=str,
              help='Workspace SUUID to list projects for a workspace')
def list(workspace_suuid):
    projects = aa_project.list(workspace_suuid)

    if not projects:
        click.echo("Based on the information provided, we cannot find any projects.")
        sys.exit(0)
    if workspace_suuid:
        click.echo(f"The projects for workspace \"{projects[0].workspace['name']}\" are:\n")
        click.echo("PROJECT SUUID          PROJECT NAME")
        click.echo("-------------------    -------------------------")
    else:
        click.echo("WORKSPACE SUUID        WORKSPACE NAME          PROJECT SUUID          PROJECT NAME")
        click.echo("-------------------    --------------------    -------------------    -------------------------")

    for project in sorted(projects, key=lambda x: (x.workspace['name'], x.name,)):
        if workspace_suuid:
            click.echo(
                "{project_suuid}    {project_name}".format(
                    project_suuid=project.short_uuid,
                    project_name=project.name[:25],
                )
            )
        else:
            click.echo(
                "{workspace_suuid}    {workspace_name}    {project_suuid}    {project_name}".format(
                    workspace_suuid=project.workspace['short_uuid'],
                    workspace_name="{:20}".format(project.workspace['name'])[:20],
                    project_suuid=project.short_uuid,
                    project_name=project.name[:25]
                )
            )


@click.group()
def cli2():
    pass


@cli2.command(help="Change project information in AskAnna", short_help="Change project")
@click.option("--id", "-i", "suuid", required=False, type=str, help="Project SUUID")
@click.option("--name", "-n", required=False, type=str, help="New name to set")
@click.option(
    "--description", "-d", required=False, type=str, help="New description to set"
)
def change(suuid, name, description):
    if not suuid:
        try:
            push_target = extract_push_target(config.push_target)
        except ValueError:
            # the push-target is not set, so don't bother reading it
            project_suuid = None
        else:
            project_suuid = push_target.get("project_suuid")

        if not project_suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to change a project?")
            project = ask_which_project(question="Which project do you want to change?",
                                        workspace_suuid=workspace.short_uuid)
            project_suuid = project.short_uuid
        suuid = project_suuid

    if not name and not description:
        if click.confirm("\nDo you want to change the name of the project?"):
            name = click.prompt("New name of the project", type=str)
        if click.confirm("\nDo you want to change the description of the project?"):
            description = click.prompt("New description of the project", type=str)

        click.confirm("\nDo you want to change the project?", abort=True)

    aa_project.change(suuid=suuid, name=name, description=description)


cli = click.CommandCollection(
    sources=[
        cli1,
        cli2,
    ],
    help="Manage your projects in AskAnna",
    short_help="Manage projects in AskAnna",
)
