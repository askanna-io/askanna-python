"""
Management of workspaces in AskAnna
This is the class which act as gateway to the API of AskAnna
"""
import sys

from askanna.core import client, exceptions
from askanna.core.dataclasses import Workspace

import click


class WorkspaceGateway:
    def __init__(self, *args, **kwargs):
        self.client = client

    def list(self) -> list:
        # build url to select for project only
        url = "{}{}/".format(
            self.client.config.remote,
            "workspace",
        )

        r = self.client.get(url)
        if r.status_code != 200:
            raise exceptions.GetError(
                "{} - Something went wrong while retrieving "
                "workspaces: {}".format(r.status_code, r.json())
            )

        return [Workspace(**workspace) for workspace in r.json()]

    def change(
        self, suuid: str, name: str = None, description: str = None
    ) -> Workspace:
        """
        Change the workspace information
        """
        url = "{}{}/{}/".format(self.client.config.remote, "workspace", suuid)

        changes = [
            ["name", name],
            ["description", description],
        ]
        # filterout None's
        changes = list(filter(lambda x: x[1] is not None, changes))
        if len(changes) == 0:
            click.echo(
                "Nothing to change for this workspace. You did not provide a name or description.",
                err=True,
            )
            sys.exit(1)

        r = self.client.patch(url, json=dict(changes))
        if r.status_code == 200:
            workspace = Workspace(**r.json())
            click.echo(f"You have successfully changed the workspace: {workspace.name}")
            return workspace
        else:
            raise exceptions.PatchError(
                "{} - Something went wrong while updating the workspace information: "
                "{}".format(r.status_code, r.json())
            )
