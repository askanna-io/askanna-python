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
        self.base_url = self.client.config.remote + "project/"

    def list(self, workspace_suuid: str = None) -> list:
        if not workspace_suuid and self.workspace:
            workspace_suuid = self.workspace.short_suuid

        if workspace_suuid:
            # build url to select for project only
            url = "{}{}/{}/{}".format(
                self.client.config.remote,
                "workspace",
                workspace_suuid,
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

    def detail(self, suuid: str) -> Project:
        url = "{}{}/".format(self.base_url, suuid)
        r = self.client.get(url)

        if r.status_code != 200:
            raise exceptions.GetError("{} - Something went wrong while retrieving "
                                      "project info: {}".format(r.status_code, r.json()))

        return Project(**r.json())
