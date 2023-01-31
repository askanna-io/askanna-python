from typing import List, Optional

from askanna.core.dataclasses.base import VISIBILITY
from askanna.core.dataclasses.project import Project
from askanna.core.exceptions import CreateError, DeleteError, GetError, PatchError
from askanna.gateways.api_client import client

from .utils import ListResponse


class ProjectListResponse(ListResponse):
    def __init__(self, data: dict):
        super().__init__(data)
        self.results: List[Project] = [Project.from_dict(project) for project in data["results"]]

    @property
    def projects(self):
        return self.results


class ProjectGateway:
    """Management of projects in AskAnna
    This is the class which act as the gateway to the API of AskAnna
    """

    def list(
        self,
        workspace_suuid: Optional[str] = None,
        page_size: Optional[int] = None,
        cursor: Optional[str] = None,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
        is_member: Optional[bool] = None,
        visibility: Optional[VISIBILITY] = None,
    ) -> ProjectListResponse:
        """List all projects with filter and order options

        Args:
            workspace_suuid (str, optional): Workspace SUUID to filter for projects in a workspace. Defaults to None.
            page_size (int, optional): Number of results per page. Defaults to the default value of the backend.
            cursor (str, optional): Cursor to start the page from. Defaults to None.
            order_by (str, optional): Order by field(s). Defaults to the default value of the backend.
            search (str, optional): Search for a specific project.
            is_member (bool, optional): Filter on projects where the authenticated user is a member.
            visibility ("PRIVATE" or "PUBLIC", optional): Filter on projects with a specific visibility.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            ProjectListResponse: The response from the API with a list of projects and pagination information.
        """
        assert page_size is None or page_size > 0, "page_size must be a positive integer"
        assert is_member is None or isinstance(is_member, bool), "is_member must be a boolean"
        if visibility is not None:
            visibility = visibility.lower()  # type: ignore
            assert visibility in ["public", "private"], "visibility must be 'public' or 'private'"

        response = client.get(
            url=client.askanna_url.project.project_list(),
            params={
                "workspace_suuid": workspace_suuid,
                "page_size": page_size,
                "cursor": cursor,
                "order_by": order_by,
                "search": search,
                "is_member": is_member,
                "visibility": visibility,
            },
        )

        if response.status_code != 200:
            error_message = f"{response.status_code} - Something went wrong while retrieving the project list"
            try:
                error_message += f":\n  {response.json()}"
            except ValueError:
                pass
            raise GetError(error_message)

        return ProjectListResponse(response.json())

    def detail(self, project_suuid: str) -> Project:
        """Get information of a project

        Args:
            project_suuid (str): SUUID of the project

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Project: Project information in a Project dataclass
        """
        response = client.get(
            url=client.askanna_url.project.project_detail(project_suuid=project_suuid),
        )

        if response.status_code == 404:
            raise GetError(f"404 - The project SUUID '{project_suuid}' was not found")
        if response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving project SUUID '{project_suuid}': "
                f"{response.json()}"
            )

        return Project.from_dict(response.json())

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
        if visibility and visibility not in ["PUBLIC", "PRIVATE"]:
            raise ValueError("Visibility must be either PUBLIC or PRIVATE")

        response = client.create(
            url=client.askanna_url.project.project(),
            json={
                "workspace_suuid": workspace_suuid,
                "name": name,
                "description": description,
                "visibility": visibility,
            },
        )

        if response.status_code != 201:
            raise CreateError(
                f"{response.status_code} - Something went wrong while creating the project: {response.json()}"
            )

        return Project.from_dict(response.json())

    def change(
        self,
        project_suuid: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> Project:
        """Change the name, description and/or visibility of a project

        Args:
            project_suuid (str): SUUID of the project to change
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

        changes = {}
        if name:
            changes.update({"name": name})
        if description:
            changes.update({"description": description})
        if visibility:
            if visibility not in ["PUBLIC", "PRIVATE"]:
                raise ValueError("Visibility must be either PUBLIC or PRIVATE")
            changes.update({"visibility": visibility})

        if not changes:
            raise ValueError("At least one of the parameters 'name', 'description' or 'visibility' must be set.")

        response = client.patch(
            url=client.askanna_url.project.project_detail(project_suuid=project_suuid),
            json=changes,
        )

        if response.status_code == 404:
            raise PatchError(f"404 - The project SUUID '{project_suuid}' was not found")
        if response.status_code != 200:
            raise PatchError(
                f"{response.status_code} - Something went wrong while updating the project SUUID '{project_suuid}': "
                f"{response.json()}"
            )

        return Project.from_dict(response.json())

    def delete(self, project_suuid: str) -> bool:
        """Delete a project

        Args:
            project_suuid (str): SUUID of the project you want to delete

        Raises:
            DeleteError: Error based on response status code with the error message from the API

        Returns:
            bool: True if the project was succesfully deleted
        """
        response = client.delete(
            url=client.askanna_url.project.project_detail(project_suuid),
        )

        if response.status_code == 404:
            raise DeleteError(f"404 - The project SUUID '{project_suuid}' was not found")
        if response.status_code != 204:
            raise DeleteError(
                f"{response.status_code} - Something went wrong while deleting the project SUUID '{project_suuid}': "
                f"{response.json()}"
            )

        return True
