# -*- coding: utf-8 -*-
import sys

import click

from askanna import workspace as aa_workspace
from askanna.cli.utils import ask_which_workspace
from askanna.config import config


@click.group()
def cli1():
    pass


@cli1.command(help="List workspaces available in AskAnna", short_help="List workspaces")
def list():
    workspaces = aa_workspace.list()

    if not workspaces:
        click.echo("Based on the information provided, we cannot find any workspaces.")
        sys.exit(0)
    else:
        click.echo("WORKSPACE SUUID        WORKSPACE NAME")
        click.echo("-------------------    -------------------------")

    for workspace in sorted(workspaces, key=lambda x: (x.name,)):
        click.echo(
            "{workspace_suuid}    {workspace_name}".format(
                workspace_suuid=workspace.short_uuid,
                workspace_name=workspace.name[:25],
            )
        )


@cli1.command(help="Change workspace information in AskAnna", short_help="Change workspace")
@click.option("--id", "-i", "suuid", required=False, type=str, help="Workspace SUUID")
@click.option("--name", "-n", required=False, type=str, help="New name to set")
@click.option("--description", "-d", required=False, type=str, help="New description to set")
@click.option("--visibility", "-v", required=False, type=str, help="New visibility to set (PRIVATE or PUBLIC)")
def change(suuid, name, description, visibility):
    if not suuid:
        suuid = config.project.workspace_suuid
        if not suuid:
            workspace = ask_which_workspace(question="Which workspace do you want to change?")
            suuid = workspace.short_uuid

    if not name and not description and not visibility:
        if click.confirm("\nDo you want to change the name of the workspace?"):
            name = click.prompt("New name of the workspace", type=str)
        if click.confirm("\nDo you want to change the description of the workspace?"):
            description = click.prompt("New description of the workspace", type=str)
        if click.confirm("\nDo you want to change the visibility of the workspace?"):
            visibility = click.prompt("Visibility of the workspace (PRIVATE or PUBLIC)", type=str)

        click.confirm("\nDo you want to change the workspace?", abort=True)

    aa_workspace.change(suuid=suuid, name=name, description=description, visibility=visibility)


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
    """
    Create a new workspace in AskAnna
    """
    confirm = False
    if not name:
        name = click.prompt("\nName of the workspace", type=str)
        confirm = True

    if not description and confirm:
        description = click.prompt(
            "Optional description of the new workspace", type=str, default="", show_default=False
        )

    if confirm:
        click.confirm(f'\nDo you want to create the workspace "{name}"?', abort=True)

    workspace, created = aa_workspace.create(name=name, description=description, visibility=visibility)
    if created:
        click.echo(f'\nYou created workspace "{workspace.name}" with SUUID {workspace.short_uuid}')
        sys.exit(0)
    else:
        click.echo("Something went wrong in creating the workspace.", err=True)
        sys.exit(1)


@cli1.command(help="Remove a workspace in AskAnna", short_help="Remove workspace")
@click.option("--id", "-i", "suuid", type=str, required=True, help="Workspace SUUID")
@click.option("--force", "-f", is_flag=True, help="Force")
def remove(suuid, force):
    """
    Remove a workspace in AskAnna
    """
    try:
        workspace = aa_workspace.detail(suuid=suuid)
    except TypeError:
        click.echo(f"It seems that a workspace {suuid} doesn't exist.", err=True)
        sys.exit(1)

    if not force:
        if not click.confirm(f'Are you sure to remove workspace {suuid} with name "{workspace.name}"?'):
            click.echo("Understood. We are not removing the workspace.")
            sys.exit(0)

    removed = aa_workspace.delete(suuid=suuid)
    if removed:
        click.echo(f"You removed workspace {suuid}")
    else:
        click.echo("Something went wrong. Removing the workspace not performed.", err=True)


cli = click.CommandCollection(
    sources=[cli1],
    help="Manage your workspaces in AskAnna",
    short_help="Manage workspaces in AskAnna",
)
