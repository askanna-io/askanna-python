"""
Management of workspaces in AskAnna
This is the class which act as gateway to the API of AskAnna
"""
import sys
from typing import Tuple, Union

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
                "{} - Something went wrong while retrieving workspaces: {}".format(r.status_code, r.json())
            )

        return [Workspace(**workspace) for workspace in r.json()]

    def detail(self, suuid: str) -> Workspace:
        url = f"{self.base_url}{suuid}/"
        r = self.client.get(url)
        return Workspace(**r.json())

    def create(
        self, name: str, description: str = "", visibility: str = "PRIVATE"
    ) -> Tuple[Union[Workspace, None], bool]:
        url = self.base_url

        if visibility and visibility not in ["PRIVATE", "PUBLIC"]:
            raise ValueError("Visibility must be either PRIVATE or PUBLIC")

        r = self.client.create(
            url,
            json={
                "name": name,
                "description": description,
                "visibility": visibility,
            },
        )
        if r.status_code == 201:
            return Workspace(**r.json()), True
        return None, False

    def change(self, suuid: str, name: str = None, description: str = None, visibility: str = None) -> Workspace:
        """
        Change the workspace information
        """
        url = f"{self.base_url}{suuid}/"

        if visibility and visibility not in ["PRIVATE", "PUBLIC"]:
            raise ValueError("Visibility must be either PRIVATE or PUBLIC")

        changes = [
            ["name", name],
            ["description", description],
            ["visibility", visibility],
        ]
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

    def delete(self, suuid: str) -> bool:
        url = f"{self.base_url}{suuid}/"
        r = self.client.delete(url)
        return r.status_code == 204
