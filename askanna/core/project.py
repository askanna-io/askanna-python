"""
Management of projects in AskAnna
This is the class which act as gateway to the API of AskAnna
"""

from askanna.core import client, exceptions
from askanna.core.dataclasses import Project


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
