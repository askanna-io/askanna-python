"""
Management of workspaces in AskAnna
This is the class which act as gateway to the API of AskAnna
"""
from askanna.core import client, exceptions
from askanna.core.dataclasses import Workspace


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
            raise exceptions.GetError("{} - Something went wrong while retrieving "
                                      "workspaces: {}".format(r.status_code, r.json()))

        return [Workspace(**workspace) for workspace in r.json()]
