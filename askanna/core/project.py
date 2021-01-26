"""
Management of projects in AskAnna
This is the class which act as gateway to the API of AskAnna
"""
from dataclasses import dataclass
import datetime
import uuid

from askanna.core import client, exceptions


@dataclass
class Project:
    name: str
    description: str
    uuid: uuid.UUID
    short_uuid: str
    created_by: dict
    package: dict
    status: int
    template: str
    created: datetime.datetime
    modified: datetime.datetime
    # deleted: datetime.datetime
    workspace: dict

    def __str__(self):
        return f'{self.name} {self.short_uuid}'


class ProjectGateway:
    def __init__(self, *args, **kwargs):
        self.client = client
        self.workspace = kwargs.get('workspace')

    def list(self, workspace=None) -> list:
        workspace = workspace or self.workspace
        if workspace:
            # build url to select for project only
            url = "{}{}/{}/{}".format(
                self.client.config.remote,
                "workspace",
                workspace.short_uuid,
                "projects"
            )
        else:
            url = "{}{}/".format(
                self.client.config.remote,
                "project"
            )

        r = self.client.get(url)
        if r.status_code != 200:
            raise exceptions.GetError("{} - Something went wrong while retrieving "
                                      "projects: {}".format(r.status_code, r.json()))

        return [Project(**project) for project in r.json()]
