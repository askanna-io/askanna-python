from typing import List, Optional

from askanna.core.dataclasses.base import VISIBILITY
from askanna.core.dataclasses.workspace import Workspace
from askanna.core.exceptions import CreateError, DeleteError, GetError, PatchError
from askanna.gateways.api_client import client

from .utils import ListResponse


class WorkspaceListResponse(ListResponse):
    def __init__(self, data: dict):
        super().__init__(data)
        self.results: List[Workspace] = [Workspace.from_dict(workspace) for workspace in data["results"]]

    @property
    def workspaces(self):
        return self.results


class WorkspaceGateway:
    """Management of workspaces in AskAnna
    This is the class which act as the gateway to the API of AskAnna
    """

    def list(
        self,
        page_size: Optional[int] = None,
        cursor: Optional[str] = None,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
        is_member: Optional[bool] = None,
        visibility: Optional[VISIBILITY] = None,
    ) -> WorkspaceListResponse:
        """List all workspaces

        Args:
            page_size (int, optional): Number of workspaces to return per page. Defaults to the default value of
                the backend.
            cursor (str, optional): Cursor to start the page from. Defaults to None.
            order_by (str, optional): Order by field(s). Defaults to the default value of the backend.
            search (str, optional): Search for a specific workspace.
            is_member (bool, optional): Filter on workspaces where the authenticated user is a member.
            visibility ("PRIVATE" or "PUBLIC", optional): Filter on workspaces with a specific visibility.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            WorkspaceListResponse: The response from the API with a list of workspaces and pagination information.
        """
        assert page_size is None or page_size > 0, "page_size must be a positive integer"
        assert is_member is None or isinstance(is_member, bool), "is_member must be a boolean"
        if visibility is not None:
            visibility = visibility.lower()  # type: ignore
            assert visibility in ["public", "private"], "visibility must be 'public' or 'private'"

        response = client.get(
            url=client.askanna_url.workspace.workspace_list(),
            params={
                "page_size": page_size,
                "cursor": cursor,
                "order_by": order_by,
                "search": search,
                "is_member": is_member,
                "visibility": visibility,
            },
        )

        if response.status_code != 200:
            error_message = f"{response.status_code} - Something went wrong while retrieving the workspace list"
            try:
                error_message += f":\n  {response.json()}"
            except ValueError:
                pass
            raise GetError(error_message)

        return WorkspaceListResponse(response.json())

    def detail(self, workspace_suuid: str) -> Workspace:
        """Get information of a workspace

        Args:
            workspace_suuid (str): SUUID of the workspace

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Workspace: Workspace information in a Workspace dataclass
        """
        response = client.get(
            url=client.askanna_url.workspace.workspace_detail(workspace_suuid=workspace_suuid),
        )

        if response.status_code == 404:
            raise GetError(f"404 - The workspace SUUID '{workspace_suuid}' was not found")
        elif response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving workspace SUUID '{workspace_suuid}': "
                f"{response.json()}"
            )

        return Workspace.from_dict(response.json())

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

        response = client.create(
            url=client.askanna_url.workspace.workspace(),
            json={
                "name": name,
                "description": description,
                "visibility": visibility,
            },
        )

        if response.status_code == 201:
            return Workspace.from_dict(response.json())
        else:
            raise CreateError(
                f"{response.status_code} - Something went wrong while creating the workspace: {response.json()}"
            )

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

        response = client.patch(
            url=client.askanna_url.workspace.workspace_detail(workspace_suuid),
            json=changes,
        )

        if response.status_code == 200:
            return Workspace.from_dict(response.json())
        else:
            raise PatchError(
                f"{response.status_code} - Something went wrong while updating the workspace SUUID "
                f"'{workspace_suuid}': {response.json()}"
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
        response = client.delete(
            url=client.askanna_url.workspace.workspace_detail(workspace_suuid),
        )

        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            raise DeleteError(f"404 - The workspace SUUID '{workspace_suuid}' was not found")
        else:
            raise DeleteError(
                f"{response.status_code} - Something went wrong while deleting the workspace SUUID "
                f"'{workspace_suuid}': {response.json()}"
            )
