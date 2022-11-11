import sys

import click

from askanna import project as aa_project
from askanna.cli.utils import ask_which_project, ask_which_workspace
from askanna.config import config
from askanna.core.exceptions import GetError, PatchError


@click.group()
def cli1():
    pass


@cli1.command(help="List projects available in AskAnna", short_help="List projects")
@click.option(
    "--workspace",
    "-w",
    "workspace_suuid",
    required=False,
    type=str,
    help="Workspace SUUID to list projects for a workspace",
)
def list(workspace_suuid):
    try:
        projects = aa_project.list(workspace_suuid=workspace_suuid)
    except Exception as e:
        click.echo(f"Something went wrong while listing the projects:\n  {e}", err=True)
        sys.exit(1)

    if not projects:
        click.echo("We cannot find any project.")
    if workspace_suuid:
        click.echo(f"The projects for workspace '{projects[0].workspace.name}' are:\n")
        click.echo("PROJECT SUUID          PROJECT NAME")
        click.echo("-------------------    -------------------------")
    else:
        click.echo("WORKSPACE SUUID        WORKSPACE NAME          PROJECT SUUID          PROJECT NAME")
        click.echo("-------------------    --------------------    -------------------    -------------------------")

    for project in sorted(projects, key=lambda x: (x.workspace.name, x.name)):
        if workspace_suuid:
            click.echo(f"{project.suuid}    {project.name[:25]}")
        else:
            click.echo(
                "{workspace_suuid}    {workspace_name}    {project_suuid}    {project_name}".format(
                    workspace_suuid=project.workspace.suuid,
                    workspace_name=f"{project.workspace.name:20}"[:20],
                    project_suuid=project.suuid,
                    project_name=project.name[:25],
                )
            )


@cli1.command(help="Change project information in AskAnna", short_help="Change project")
@click.option("--id", "-i", "suuid", required=False, type=str, help="Project SUUID")
@click.option("--name", "-n", required=False, type=str, help="New name to set")
@click.option("--description", "-d", required=False, type=str, help="New description to set")
@click.option("--visibility", "-v", required=False, type=str, help="New visibility to set (PRIVATE or PUBLIC)")
def change(suuid, name, description, visibility):
    if not suuid:
        suuid = config.project.project_suuid
        if not suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to change a project?")
            project = ask_which_project(
                question="Which project do you want to change?", workspace_suuid=workspace.suuid
            )
            suuid = project.suuid

    if not name and not description and not visibility:
        if click.confirm("\nDo you want to change the name of the project?"):
            name = click.prompt("New name of the project", type=str)
        if click.confirm("\nDo you want to change the description of the project?"):
            description = click.prompt("New description of the project", type=str)
        if click.confirm("\nDo you want to change the visibility of the project?"):
            visibility = click.prompt("Visibility of the project (PRIVATE or PUBLIC)", type=str)

        click.confirm("\nDo you want to change the project?", abort=True)

    try:
        project = aa_project.change(suuid=suuid, name=name, description=description, visibility=visibility)
    except PatchError as e:
        if str(e).startswith("404"):
            click.echo(f"The project SUUID '{suuid}' was not found", err=True)
            sys.exit(1)
        else:
            click.echo(f"Something went wrong while changing the project SUUID '{suuid}':\n  {e}", err=True)
            sys.exit(1)
    else:
        click.echo(f"\nYou succesfully changed project '{project.name}' with SUUID '{project.suuid}'")


@cli1.command(help="Create a new project in AskAnna", short_help="Create project")
@click.option(
    "--workspace",
    "-w",
    "workspace_suuid",
    type=str,
    help="Workspace SUUID where you want to create the project",
)
@click.option("--name", "-n", required=False, type=str, help="Name of the project")
@click.option("--description", "-d", required=False, type=str, help="Description of the project")
@click.option(
    "--visibility",
    "-v",
    required=False,
    type=str,
    default="PRIVATE",
    help="Project visibility (PRIVATE (default) or PUBLIC)",
)
def create(workspace_suuid, name, description, visibility):
    if not workspace_suuid:
        workspace = ask_which_workspace("In which workspace do you want to create the new project?")
        workspace_suuid = workspace.suuid

    if not name:
        name = click.prompt("\nName of the project", type=str)

        if not description:
            description = click.prompt("Optional description of the project", type=str, default="", show_default=False)

    click.confirm(f'\nDo you want to create the project "{name}"?', abort=True)

    try:
        project = aa_project.create(
            workspace_suuid=workspace_suuid, name=name, description=description, visibility=visibility
        )
    except Exception as e:
        click.echo(f"Something went wrong while creating the project:\n  {e}", err=True)
        sys.exit(1)
    else:
        click.echo(f"\nYou successfully created project '{project.name}' with SUUID '{project.suuid}'")


@cli1.command(help="Remove a project in AskAnna", short_help="Remove project")
@click.option("--id", "-i", "suuid", type=str, required=True, help="Project SUUID", prompt="Project SUUID")
@click.option("--force", "-f", is_flag=True, help="Force")
def remove(suuid, force):
    try:
        project = aa_project.detail(suuid=suuid)
    except GetError as e:
        if str(e).startswith("404"):
            click.echo(f"The project SUUID '{suuid}' was not found", err=True)
            sys.exit(1)
        else:
            click.echo(f"Something went wrong while removing the project SUUID '{suuid}':\n  {e}", err=True)
            sys.exit(1)

    if not force:
        if not click.confirm(f"Are you sure to remove project SUUID '{suuid}' with name '{project.name}'?"):
            click.echo("Understood. We are not removing the project.")
            sys.exit(0)

    try:
        removed = aa_project.delete(suuid=suuid)
    except Exception as e:
        click.echo(f"Something went wrong while removing the project SUUID '{suuid}':\n  {e}", err=True)
        sys.exit(1)
    else:
        if removed:
            click.echo(f"You removed project SUUID '{suuid}'")
        else:
            click.echo(f"Something went wrong. Removing the project SUUID '{suuid}' aborted.", err=True)
            sys.exit(1)


cli = click.CommandCollection(
    sources=[cli1],
    help="Manage your projects in AskAnna",
    short_help="Manage projects in AskAnna",
)
