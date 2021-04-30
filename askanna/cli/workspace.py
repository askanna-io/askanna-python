# -*- coding: utf-8 -*-
import click
import sys

from askanna import workspace as aa_workspace
from askanna.cli.utils import ask_which_workspace
from askanna.core.config import Config
from askanna.core.utils import extract_push_target


config = Config()


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


@click.group()
def cli2():
    pass


@cli2.command(
    help="Change workspace information in AskAnna", short_help="Change workspace"
)
@click.option("--id", "-i", "suuid", required=False, type=str, help="Workspace SUUID")
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
            workspace_suuid = None
        else:
            workspace_suuid = push_target.get("workspace_suuid")

        if not workspace_suuid:
            workspace = ask_which_workspace(
                question="Which workspace do you want to change?"
            )
            workspace_suuid = workspace.short_uuid
        suuid = workspace_suuid

    if not name and not description:
        if click.confirm("\nDo you want to change the name of the workspace?"):
            name = click.prompt("New name of the workspace", type=str)
        if click.confirm("\nDo you want to change the description of the workspace?"):
            description = click.prompt("New description of the workspace", type=str)

        click.confirm("\nDo you want to change the workspace?", abort=True)

    aa_workspace.change(suuid=suuid, name=name, description=description)


cli = click.CommandCollection(
    sources=[
        cli1,
        cli2,
    ],
    help="Manage your workspaces in AskAnna",
    short_help="Manage workspaces in AskAnna",
)
