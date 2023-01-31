from typing import List, Optional

from askanna.core.dataclasses.base import VISIBILITY
from askanna.core.dataclasses.workspace import Workspace
from askanna.gateways.workspace import WorkspaceGateway

from .mixins import ListMixin

__all__ = [
    "WorkspaceSDK",
]


class WorkspaceSDK(ListMixin):
    """Management of workspaces in AskAnna
    This class is a wrapper around the WorkspaceGateway and can be used to manage workspaces in Python.
    """

    gateway = WorkspaceGateway()

    def list(
        self,
        number_of_results: int = 100,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
        is_member: Optional[bool] = None,
        visibility: Optional[VISIBILITY] = None,
    ) -> List[Workspace]:
        """List all workspaces

        Args:
            number_of_results (int): Number of workspaces to return. Defaults to 100.
            order_by (str, optional): Order by field(s).
            search (str, optional): Search for a specific workspace.
            is_member (bool, optional): Filter on workspaces where the authenticated user is a member.
            visibility ("PRIVATE" or "PUBLIC", optional): Filter on workspaces with a specific visibility.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            List[Workspace]: A list of workspaces. List items are of type Workspace dataclass.
        """
        return super().list(
            number_of_results=number_of_results,
            order_by=order_by,
            other_query_params={
                "search": search,
                "is_member": is_member,
                "visibility": visibility,
            },
        )

    def get(self, workspace_suuid: str) -> Workspace:
        """Get information of a workspace

        Args:
            workspace_suuid (str): SUUID of the workspace

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Workspace: Workspace information in a Workspace dataclass
        """
        return self.gateway.detail(workspace_suuid)

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
        return self.gateway.create(
            name=name,
            description=description,
            visibility=visibility,
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
        return self.gateway.change(
            workspace_suuid=workspace_suuid,
            name=name,
            description=description,
            visibility=visibility,
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
        return self.gateway.delete(workspace_suuid)
