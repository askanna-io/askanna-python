import sys

import click

from askanna.cli.utils import ask_which_workspace
from askanna.config import config
from askanna.core.exceptions import GetError, PatchError
from askanna.sdk.workspace import WorkspaceSDK


@click.group()
def cli1():
    pass


@cli1.command(help="List workspaces available in AskAnna", short_help="List workspaces")
@click.option("--search", "-s", required=False, type=str, help="Search for a specific workspace")
@click.option(
    "--member/--no-member",
    "-m",
    "is_member",
    default=None,
    required=False,
    type=bool,
    help="Filter on workspaces where the authenticated user is a member.",
)
@click.option(
    "--visibility", "-v", required=False, type=str, help="Filter on workspaces with visibility private or public"
)
def list(search, is_member, visibility):
    workspace_sdk = WorkspaceSDK()
    try:
        workspaces = workspace_sdk.list(
            number_of_results=100,
            search=search,
            is_member=is_member,
            visibility=visibility,
            order_by="name",
        )
    except Exception as e:
        click.echo(f"Something went wrong while listing the workspaces:\n  {e}", err=True)
        sys.exit(1)

    if not workspaces:
        click.echo("We cannot find any workspaces.")
        sys.exit(0)

    click.echo("")
    click.echo("-------------------    -------------------------")
    click.echo("WORKSPACE SUUID        WORKSPACE NAME")
    click.echo("-------------------    -------------------------")

    for workspace in workspaces:
        workspace_name = f"{workspace.name[:22]}..." if len(workspace.name) > 25 else workspace.name[:25]
        click.echo(f"{workspace.suuid}    {workspace_name}")

    if len(workspaces) != workspace_sdk.list_total_count:
        click.echo("")
        click.echo(f"Note: the first {len(workspaces):,} of {workspace_sdk.list_total_count:,} workspaces are shown.")

    click.echo("")


@cli1.command(help="Get information about a workspace", short_help="Get workspace info")
@click.option("--id", "-i", "workspace_suuid", required=False, type=str, help="Workspace SUUID")
def info(workspace_suuid):
    if not workspace_suuid:
        workspace_suuid = config.project.workspace_suuid

    if workspace_suuid:
        try:
            workspace = WorkspaceSDK().get(workspace_suuid)
        except GetError as e:
            click.echo(f"Something went wrong while getting the workspace:\n  {e}", err=True)
            sys.exit(1)
    else:
        workspace = ask_which_workspace(question="Which workspace do you want to get?")

    click.echo("")
    click.echo(f"Name:        {workspace.name}")
    click.echo(f"SUUID:       {workspace.suuid}")
    click.echo(f"Description: {workspace.description}")
    click.echo(f"Visibility:  {workspace.visibility}")
    click.echo("")
    click.echo(f"Created:  {workspace.created}")
    click.echo(f"Modified: {workspace.modified}")
    click.echo("")


@cli1.command(help="Change workspace information in AskAnna", short_help="Change workspace")
@click.option("--id", "-i", "workspace_suuid", required=False, type=str, help="Workspace SUUID")
@click.option("--name", "-n", required=False, type=str, help="New name to set")
@click.option("--description", "-d", required=False, type=str, help="New description to set")
@click.option("--visibility", "-v", required=False, type=str, help="New visibility to set (PRIVATE or PUBLIC)")
def change(workspace_suuid, name, description, visibility):
    if not workspace_suuid:
        workspace_suuid = config.project.workspace_suuid
        if not workspace_suuid:
            workspace = ask_which_workspace(question="Which workspace do you want to change?")
            workspace_suuid = workspace.suuid

    if not name and not description and not visibility:
        if click.confirm("\nDo you want to change the name of the workspace?"):
            name = click.prompt("New name of the workspace", type=str)
        if click.confirm("\nDo you want to change the description of the workspace?"):
            description = click.prompt("New description of the workspace", type=str)
        if click.confirm("\nDo you want to change the visibility of the workspace?"):
            visibility = click.prompt("Visibility of the workspace (PRIVATE or PUBLIC)", type=str)

        click.confirm("\nDo you want to change the workspace?", abort=True)

    try:
        workspace = WorkspaceSDK().change(
            workspace_suuid=workspace_suuid, name=name, description=description, visibility=visibility
        )
    except PatchError as e:
        if str(e).startswith("404"):
            click.echo(f"The workspace SUUID '{workspace_suuid}' was not found", err=True)
            sys.exit(1)
        else:
            click.echo(
                f"Something went wrong while changing the workspace SUUID '{workspace_suuid}':\n  {e}", err=True
            )
            sys.exit(1)
    else:
        click.echo(f"\nYou succesfully changed workspace '{workspace.name}' with SUUID '{workspace.suuid}'")


@cli1.command(help="Create a new workspace in AskAnna", short_help="Create workspace")
@click.option("--name", "-n", required=False, type=str, help="Name of the workspace")
@click.option("--description", "-d", required=False, type=str, help="Description of the workspace")
@click.option(
    "--visibility",
    "-v",
    required=False,
    type=str,
    default="PRIVATE",
    help="Workspace visibility (PRIVATE (default) or PUBLIC)",
)
def create(name, description, visibility):
    if not name:
        name = click.prompt("\nName of the workspace", type=str)

        if not description:
            description = click.prompt(
                "Optional description of the workspace", type=str, default="", show_default=False
            )

    click.confirm(f'\nDo you want to create the workspace "{name}"?', abort=True)

    try:
        workspace = WorkspaceSDK().create(name=name, description=description, visibility=visibility)
    except Exception as e:
        click.echo(f"Something went wrong while creating the workspace:\n  {e}", err=True)
        sys.exit(1)
    else:
        click.echo(f"\nYou successfully created workspace '{workspace.name}' with SUUID '{workspace.suuid}'")


@cli1.command(help="Remove a workspace in AskAnna", short_help="Remove workspace")
@click.option(
    "--id", "-i", "workspace_suuid", type=str, required=True, help="Workspace SUUID", prompt="Workspace SUUID"
)
@click.option("--force", "-f", is_flag=True, help="Force")
def remove(workspace_suuid, force):
    try:
        workspace = WorkspaceSDK().get(workspace_suuid)
    except GetError as e:
        if str(e).startswith("404"):
            click.echo(f"The workspace SUUID '{workspace_suuid}' was not found", err=True)
            sys.exit(1)
        else:
            click.echo(
                f"Something went wrong while removing the workspace SUUID '{workspace_suuid}':\n  {e}", err=True
            )
            sys.exit(1)

    if not force:
        if not click.confirm(
            f"Are you sure to remove workspace SUUID '{workspace_suuid}' with name '{workspace.name}'?"
        ):
            click.echo("Understood. We are not removing the workspace.")
            sys.exit(0)

    try:
        removed = WorkspaceSDK().delete(workspace_suuid)
    except Exception as e:
        click.echo(f"Something went wrong while removing the workspace SUUID '{workspace_suuid}':\n  {e}", err=True)
        sys.exit(1)
    else:
        if removed:
            click.echo(f"You removed workspace SUUID '{workspace_suuid}'")
        else:
            click.echo(f"Something went wrong. Removing the workspace SUUID '{workspace_suuid}' aborted.", err=True)
            sys.exit(1)


cli = click.CommandCollection(
    sources=[cli1],
    help="Manage your workspaces in AskAnna",
    short_help="Manage workspaces in AskAnna",
)
