from typing import List, Optional

from askanna.core.dataclasses.workspace import Workspace
from askanna.core.exceptions import CreateError, DeleteError, GetError, PatchError
from askanna.gateways.api_client import client


class WorkspaceGateway:
    """Management of workspaces in AskAnna
    This is the class which act as the gateway to the API of AskAnna
    """

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        ordering: str = "-created",
    ) -> List[Workspace]:
        """List all workspaces

        Args:
            limit (int): Number of results to return. Defaults to 100.
            offset (int): The initial index from which to return the results. Defaults to 0.
            ordering (str): The ordering of the results. Defaults to "-created".

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            List[Workspace]: A list of workspaces. List items are of type Workspace dataclass.
        """
        query = {
            "offset": offset,
            "limit": limit,
            "ordering": ordering,
        }

        url = client.askanna_url.workspace.workspace_list()
        r = client.get(url, params=query)

        if r.status_code != 200:
            raise GetError(f"{r.status_code} - Something went wrong while retrieving workspaces: {r.json()}")

        return [Workspace.from_dict(workspace) for workspace in r.json().get("results")]

    def detail(self, workspace_suuid: str) -> Workspace:
        """Get information of a workspace

        Args:
            workspace_suuid (str): SUUID of the workspace

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Workspace: Workspace information in a Workspace dataclass
        """
        url = client.askanna_url.workspace.workspace_detail(workspace_suuid)
        r = client.get(url)

        if r.status_code == 404:
            raise GetError(f"404 - The workspace SUUID '{workspace_suuid}' was not found")
        elif r.status_code != 200:
            raise GetError(
                f"{r.status_code} - Something went wrong while retrieving workspace SUUID '{workspace_suuid}': "
                f"{r.json()}"
            )

        return Workspace.from_dict(r.json())

    def create(self, name: str, description: str = "", visibility: str = "PRIVATE") -> Workspace:
        """Create a new workspace

        Args:
            name (str): Name of the new workspace
            description (str, optional): Description for the new workspace. Defaults to "" (empty string).
            visibility ("PUBLIC" or "PRIVATE", optional): Visibility of the new workspace. Defaults to "PRIVATE".

        Raises:
            ValueError: Error when visibility is not "PUBLIC" or "PRIVATE"
            CreateError: Error based on response status code with the error message from the API

        Returns:
            Workspace: The information of the newly created workspace in a Workspace dataclass
        """
        if visibility and visibility not in ["PUBLIC", "PRIVATE"]:
            raise ValueError("Visibility must be either PUBLIC or PRIVATE")

        url = client.askanna_url.workspace.workspace()
        r = client.create(
            url,
            json={
                "name": name,
                "description": description,
                "visibility": visibility,
            },
        )

        if r.status_code == 201:
            return Workspace.from_dict(r.json())
        else:
            raise CreateError(f"{r.status_code} - Something went wrong while creating the workspace: {r.json()}")

    def change(
        self,
        workspace_suuid: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> Workspace:
        """Change the name, description and/or visibility of a workspace

        Args:
            workspace_suuid (str): SUUID of the workspace you want to change the information of
            name (str, optional): New name for the workspace. Defaults to None.
            description (str, optional): New description of the workspace. Defaults to None.
            visibility ("PUBLIC" or "PRIVATE", optional): New visibility of the workspace. Defaults to None.

        Raises:
            ValueError: Error when visibility is not "PUBLIC" or "PRIVATE"
            ValueError: Error if none of the arguments 'name', 'description' or 'visibility' are provided
            PatchError: Error based on response status code with the error message from the API

        Returns:
            Workspace: The changed workspace information in a Workspace dataclass
        """
        if visibility and visibility not in ["PUBLIC", "PRIVATE"]:
            raise ValueError("Visibility must be either PUBLIC or PRIVATE")

        changes = {}
        if name:
            changes.update({"name": name})
        if description:
            changes.update({"description": description})
        if visibility:
            changes.update({"visibility": visibility})

        if not changes:
            raise ValueError("At least one of the parameters 'name', 'description' or 'visibility' must be set.")

        url = client.askanna_url.workspace.workspace_detail(workspace_suuid)
        r = client.patch(url, json=changes)

        if r.status_code == 200:
            return Workspace.from_dict(r.json())
        else:
            raise PatchError(
                f"{r.status_code} - Something went wrong while updating the workspace SUUID '{workspace_suuid}': "
                f"{r.json()}"
            )

    def delete(self, workspace_suuid: str) -> bool:
        """Delete a workspace

        Args:
            workspace_suuid (str): SUUID of the workspace you want to delete

        Raises:
            DeleteError: Error based on response status code with the error message from the API

        Returns:
            bool: True if the workspace was succesfully deleted
        """
        url = client.askanna_url.workspace.workspace_detail(workspace_suuid)
        r = client.delete(url)

        if r.status_code == 204:
            return True
        elif r.status_code == 404:
            raise DeleteError(f"404 - The workspace SUUID '{workspace_suuid}' was not found")
        else:
            raise DeleteError(
                f"{r.status_code} - Something went wrong while deleting the workspace SUUID '{workspace_suuid}': "
                f"{r.json()}"
            )
