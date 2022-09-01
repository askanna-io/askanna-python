"""
Management of projects in AskAnna
This is the class which act as gateway to the API of AskAnna
"""
import sys
from typing import List, Union

import click

from askanna.core import exceptions
from askanna.core.apiclient import client
from askanna.core.dataclasses import Package, Project


class ProjectGateway:
    def __init__(self, *args, **kwargs):
        self.workspace = kwargs.get("workspace")

    @property
    def base_url(self):
        return client.base_url + "project/"

    def list(self, workspace_suuid: str = None) -> list:
        if not workspace_suuid and self.workspace:
            workspace_suuid = self.workspace.short_suuid

        if workspace_suuid:
            # build url to select for workspace only
            url = f"{client.base_url}workspace/{workspace_suuid}/projects/"
        else:
            url = self.base_url

        r = client.get(url)
        if r.status_code != 200:
            raise exceptions.GetError(f"{r.status_code} - Something went wrong while retrieving projects: {r.json()}")

        return [Project(**project) for project in r.json()]

    def detail(self, suuid: str) -> Project:
        url = f"{self.base_url}{suuid}/"
        r = client.get(url)

        if r.status_code != 200:
            raise exceptions.GetError(
                f"{r.status_code} - Something went wrong while retrieving project info: {r.json()}"
            )

        return Project(**r.json())

    def change(self, suuid: str, name: str = None, description: str = None, visibility: str = None) -> Project:
        """
        Change the project information
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
                "Nothing to change for this project. You did not provide name, description or visibility.",
                err=True,
            )
            sys.exit(1)

        r = client.patch(url, json=dict(changes))
        if r.status_code == 200:
            project = Project(**r.json())
            click.echo(f"You have successfully changed the project: {project.name}")
            return project
        else:
            raise exceptions.PatchError(
                "{} - Something went wrong while updating the project information: "
                "{}".format(r.status_code, r.json())
            )

    def delete(self, suuid: str) -> bool:
        url = f"{self.base_url}{suuid}/"
        r = client.delete(url)
        return r.status_code == 204

    def packages(self, suuid: str, offset: Union[int, None] = None, limit: Union[int, None] = None) -> List[Package]:
        url = f"{self.base_url}{suuid}/packages/"

        query = {}
        if offset:
            query.update({"offset": offset})
        if limit:
            query.update({"limit": limit})

        r = client.get(url, params=query)

        if r.status_code != 200:
            raise exceptions.GetError(
                f"{r.status_code} - Something went wrong while retrieving project packages: {r.json()}"
            )

        if isinstance(r.json(), list):
            return [Package(**package) for package in r.json()]
        else:
            return [Package(**package) for package in r.json().get("results")]
