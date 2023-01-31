from typing import List, Optional

from askanna.core.dataclasses.base import VISIBILITY
from askanna.core.dataclasses.project import Project
from askanna.gateways.project import ProjectGateway

from .mixins import ListMixin

__all__ = [
    "ProjectSDK",
]


class ProjectSDK(ListMixin):
    """Management of projects in AskAnna
    This class is a wrapper around the ProjectGateway and can be used to manage projects in Python.
    """

    gateway = ProjectGateway()

    def list(
        self,
        workspace_suuid: Optional[str] = None,
        number_of_results: int = 100,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
        is_member: Optional[bool] = None,
        visibility: Optional[VISIBILITY] = None,
    ) -> List[Project]:
        """List all projects with filter and order options

        Args:
            workspace_suuid (str, optional): Workspace SUUID to filter for projects in a workspace. Defaults to None.
            number_of_results (int): Number of projects to return. Defaults to 100.
            order_by (str, optional): Order by field(s).
            search (str, optional): Search for a specific project.
            is_member (bool, optional): Filter on projects where the authenticated user is a member.
            visibility ("PRIVATE" or "PUBLIC", optional): Filter on projects with a specific visibility.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            List[Project]: List of projects. List items are of type Project dataclass.
        """
        return super().list(
            number_of_results=number_of_results,
            order_by=order_by,
            other_query_params={
                "workspace_suuid": workspace_suuid,
                "search": search,
                "is_member": is_member,
                "visibility": visibility,
            },
        )

    def get(self, project_suuid: str) -> Project:
        """Get information of a project

        Args:
            project_suuid (str): SUUID of the project

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Project: Project information in a Project dataclass
        """
        return self.gateway.detail(project_suuid)

    def create(self, workspace_suuid: str, name: str, description: str = "", visibility: str = "PRIVATE") -> Project:
        """Create a new project

        Args:
            workspace_suuid (str): SUUID of the workspace to create the project in
            name (str): Name of the new project
            description (str, optional): Description for the new project. Defaults to "" (empty string).
            visibility (str, optional): Visibility of the new workspace. Defaults to "PRIVATE".

        Raises:
            ValueError: Error when visibility is not "PUBLIC" or "PRIVATE"
            CreateError: Error based on response status code with the error message from the API

        Returns:
            Project: The information of the newly created project in a Project dataclass
        """
        return self.gateway.create(
            workspace_suuid=workspace_suuid,
            name=name,
            description=description,
            visibility=visibility,
        )

    def change(
        self,
        project_suuid: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> Project:
        """Change the name, description and/or visibility of a project

        Args:
            project_suuid (str): SUUID of the project you want to change the information of
            name (str, optional): New name for the project. Defaults to None.
            description (str, optional): New description of the project. Defaults to None.
            visibility ("PUBLIC" or "PRIVATE", optional): New visibility of the project. Defaults to None.

        Raises:
            ValueError: Error when visibility is not "PUBLIC" or "PRIVATE"
            ValueError: Error if none of the arguments 'name', 'description' or 'visibility' are provided
            PatchError: Error based on response status code with the error message from the API

        Returns:
            Project: The changed project information in a Project dataclass
        """
        return self.gateway.change(
            project_suuid=project_suuid,
            name=name,
            description=description,
            visibility=visibility,
        )

    def delete(self, project_suuid: str) -> bool:
        """Delete a project

        Args:
            project_suuid (str): SUUID of the project you want to delete

        Raises:
            DeleteError: Error based on response status code with the error message from the API

        Returns:
            bool: True if the project was succesfully deleted
        """
        return self.gateway.delete(project_suuid)
