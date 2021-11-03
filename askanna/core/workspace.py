"""
Management of workspaces in AskAnna
This is the class which act as gateway to the API of AskAnna
"""
import sys

import click

from askanna.core import exceptions
from askanna.core.apiclient import client
from askanna.core.dataclasses import Workspace


class WorkspaceGateway:
    def __init__(self, *args, **kwargs):
        self.client = client
        self.base_url = self.client.base_url + "workspace/"

    def list(self) -> list:
        r = self.client.get(self.base_url)

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
        url = f"{self.base_url}{suuid}/"

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
