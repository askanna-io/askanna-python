import sys

import click

from askanna.cli.utils import ask_which_project, ask_which_workspace
from askanna.config import config
from askanna.core.exceptions import GetError, PatchError
from askanna.sdk.project import ProjectSDK


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
@click.option("--search", "-s", required=False, type=str, help="Search for a specific project")
@click.option(
    "--member/--no-member",
    "-m",
    "is_member",
    default=None,
    required=False,
    type=bool,
    help="Filter on projects where the authenticated user is a member.",
)
@click.option(
    "--visibility", "-v", required=False, type=str, help="Filter on projects with visibility private or public"
)
def list(workspace_suuid, search, is_member, visibility):
    project_sdk = ProjectSDK()
    try:
        projects = project_sdk.list(
            number_of_results=100,
            workspace_suuid=workspace_suuid,
            search=search,
            is_member=is_member,
            visibility=visibility,
            order_by="workspace.name,name",
        )
    except Exception as e:
        click.echo(f"Something went wrong while listing the projects:\n  {e}", err=True)
        sys.exit(1)

    if not projects:
        click.echo("We cannot find any project.")
        sys.exit(0)

    if workspace_suuid:
        click.echo(f"The projects for workspace '{projects[0].workspace.name}' are:")
        click.echo("")
        click.echo("-------------------    -------------------------")
        click.echo("PROJECT SUUID          PROJECT NAME")
        click.echo("-------------------    -------------------------")
    else:
        click.echo("")
        click.echo("-------------------    --------------------    -------------------    -------------------------")
        click.echo("WORKSPACE SUUID        WORKSPACE NAME          PROJECT SUUID          PROJECT NAME")
        click.echo("-------------------    --------------------    -------------------    -------------------------")

    for project in projects:
        project_name = f"{project.name[:22]}..." if len(project.name) > 25 else project.name[:25]
        if workspace_suuid:
            click.echo(f"{project.suuid}    {project_name}")
        else:
            workspace_name = (
                f"{project.workspace.name[:17]}..."
                if len(project.workspace.name) > 20
                else project.workspace.name[:20]
            )
            click.echo(
                "{workspace_suuid}    {workspace_name}    {project_suuid}    {project_name}".format(
                    workspace_suuid=project.workspace.suuid,
                    workspace_name=f"{workspace_name:20}",
                    project_suuid=project.suuid,
                    project_name=project_name,
                )
            )

    if len(projects) != project_sdk.list_total_count:
        click.echo("")
        click.echo(f"Note: the first {len(projects):,} of {project_sdk.list_total_count:,} projects are shown.")

    click.echo("")


@cli1.command(help="Get information about a project", short_help="Get project info")
@click.option("--id", "-i", "project_suuid", required=False, type=str, help="Project SUUID")
def info(project_suuid):
    if not project_suuid:
        project_suuid = config.project.project_suuid

    if project_suuid:
        try:
            project = ProjectSDK().get(project_suuid=project_suuid)
        except GetError as e:
            click.echo(f"Something went wrong while getting the project:\n  {e}", err=True)
            sys.exit(1)
    else:
        workspace = ask_which_workspace(question="From which workspace do you want to get a project?")
        project = ask_which_project(question="Which project do you want to get?", workspace_suuid=workspace.suuid)

    click.echo("")
    click.echo(f"Name:        {project.name}")
    click.echo(f"SUUID:       {project.suuid}")
    click.echo(f"Description: {project.description}")
    click.echo(f"Visibility:  {project.visibility}")
    click.echo("")
    click.echo(f"Workspace:       {project.workspace.name}")
    click.echo(f"Workspace SUUID: {project.workspace.suuid}")
    click.echo("")
    click.echo(f"Created:  {project.created}")
    click.echo(f"Modified: {project.modified}")
    click.echo("")


@cli1.command(help="Change project information in AskAnna", short_help="Change project")
@click.option("--id", "-i", "project_suuid", required=False, type=str, help="Project SUUID")
@click.option("--name", "-n", required=False, type=str, help="New name to set")
@click.option("--description", "-d", required=False, type=str, help="New description to set")
@click.option("--visibility", "-v", required=False, type=str, help="New visibility to set (PRIVATE or PUBLIC)")
def change(project_suuid, name, description, visibility):
    if not project_suuid:
        project_suuid = config.project.project_suuid

        if not project_suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to change a project?")
            project = ask_which_project(
                question="Which project do you want to change?", workspace_suuid=workspace.suuid
            )
            project_suuid = project.suuid

    if not name and not description and not visibility:
        if click.confirm("\nDo you want to change the name of the project?"):
            name = click.prompt("New name of the project", type=str)
        if click.confirm("\nDo you want to change the description of the project?"):
            description = click.prompt("New description of the project", type=str)
        if click.confirm("\nDo you want to change the visibility of the project?"):
            visibility = click.prompt("Visibility of the project (PRIVATE or PUBLIC)", type=str)

        click.confirm("\nDo you want to change the project?", abort=True)

    try:
        project = ProjectSDK().change(
            project_suuid=project_suuid, name=name, description=description, visibility=visibility
        )
    except PatchError as e:
        if str(e).startswith("404"):
            click.echo(f"The project SUUID '{project_suuid}' was not found", err=True)
            sys.exit(1)
        else:
            click.echo(f"Something went wrong while changing the project SUUID '{project_suuid}':\n  {e}", err=True)
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
        project = ProjectSDK().create(
            workspace_suuid=workspace_suuid, name=name, description=description, visibility=visibility
        )
    except Exception as e:
        click.echo(f"Something went wrong while creating the project:\n  {e}", err=True)
        sys.exit(1)
    else:
        click.echo(f"\nYou successfully created project '{project.name}' with SUUID '{project.suuid}'")


@cli1.command(help="Remove a project in AskAnna", short_help="Remove project")
@click.option("--id", "-i", "project_suuid", type=str, required=True, help="Project SUUID", prompt="Project SUUID")
@click.option("--force", "-f", is_flag=True, help="Force")
def remove(project_suuid, force):
    try:
        project = ProjectSDK().get(project_suuid=project_suuid)
    except GetError as e:
        if str(e).startswith("404"):
            click.echo(f"The project SUUID '{project_suuid}' was not found", err=True)
            sys.exit(1)
        else:
            click.echo(f"Something went wrong while removing the project SUUID '{project_suuid}':\n  {e}", err=True)
            sys.exit(1)

    if not force:
        if not click.confirm(f"Are you sure to remove project SUUID '{project_suuid}' with name '{project.name}'?"):
            click.echo("Understood. We are not removing the project.")
            sys.exit(0)

    try:
        _ = ProjectSDK().delete(project_suuid=project_suuid)
    except Exception as e:
        click.echo(f"Something went wrong while removing the project SUUID '{project_suuid}':\n  {e}", err=True)
        sys.exit(1)
    else:
        click.echo(f"You removed project SUUID '{project_suuid}'")


cli = click.CommandCollection(
    sources=[cli1],
    help="Manage your projects in AskAnna",
    short_help="Manage projects in AskAnna",
)
