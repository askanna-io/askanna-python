from typing import List, Optional

from askanna.core.dataclasses.package import Package
from askanna.core.dataclasses.project import Project
from askanna.core.exceptions import CreateError, DeleteError, GetError, PatchError
from askanna.gateways.api_client import client
from askanna.gateways.package import PackageGateway


class ProjectGateway:
    """Management of projects in AskAnna
    This is the class which act as the gateway to the API of AskAnna
    """

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        workspace_suuid: Optional[str] = None,
        ordering: str = "-created",
    ) -> List[Project]:
        """List all projects with the option to filter on workspace

        Args:
            limit (int): Number of results to return. Defaults to 100.
            offset (int): The initial index from which to return the results. Defaults to 0.
            workspace_suuid (str, optional): Workspace SUUID to filter for projects in a workspace. Defaults to None.
            ordering (str): Ordering of the results. Defaults to "-created".

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            List[Project]: A list of projects. List items are of type Project dataclass.
        """
        if workspace_suuid:
            # Get URL to filter projects for a specific workspace
            url = client.askanna_url.workspace.project_list(workspace_suuid)
        else:
            # Get URL to select for all projects
            url = client.askanna_url.project.project_list()

        query = {
            "offset": offset,
            "limit": limit,
            "ordering": ordering,
        }

        r = client.get(url, params=query)

        if r.status_code != 200:
            raise GetError(f"{r.status_code} - Something went wrong while retrieving projects: {r.json()}")

        return [Project.from_dict(project) for project in r.json().get("results")]

    def detail(self, suuid: str) -> Project:
        """Get information of a project

        Args:
            suuid (str): SUUID of the project

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Project: Project information in a Project dataclass
        """
        url = client.askanna_url.project.project_detail(suuid)
        r = client.get(url)

        if r.status_code == 404:
            raise GetError(f"404 - The project SUUID '{suuid}' was not found")
        elif r.status_code != 200:
            raise GetError(
                f"{r.status_code} - Something went wrong while retrieving project SUUID '{suuid}': {r.json()}"
            )

        return Project.from_dict(r.json())

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
        url = client.askanna_url.project.project()

        if visibility and visibility not in ["PUBLIC", "PRIVATE"]:
            raise ValueError("Visibility must be either PUBLIC or PRIVATE")

        r = client.create(
            url,
            json={
                "workspace": workspace_suuid,
                "name": name,
                "description": description,
                "visibility": visibility,
            },
        )

        if r.status_code == 201:
            return Project.from_dict(r.json())
        else:
            raise CreateError(f"{r.status_code} - Something went wrong while creating the project: {r.json()}")

    def change(
        self,
        suuid: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> Project:
        """Change the name, description and/or visibility of a project

        Args:
            suuid (str): SUUID of the project you want to change the information of
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

        url = client.askanna_url.project.project_detail(suuid)
        r = client.patch(url, json=changes)

        if r.status_code == 200:
            return Project.from_dict(r.json())
        else:
            raise PatchError(
                f"{r.status_code} - Something went wrong while updating the project SUUID '{suuid}': {r.json()}"
            )

    def delete(self, suuid: str) -> bool:
        """Delete a project

        Args:
            suuid (str): SUUID of the project you want to delete

        Raises:
            DeleteError: Error based on response status code with the error message from the API

        Returns:
            bool: True if the project was succesfully deleted
        """
        url = client.askanna_url.project.project_detail(suuid)
        r = client.delete(url)

        if r.status_code == 204:
            return True
        elif r.status_code == 404:
            raise DeleteError(f"404 - The project SUUID '{suuid}' was not found")
        else:
            raise DeleteError(
                f"{r.status_code} - Something went wrong while deleting the project SUUID '{suuid}': {r.json()}"
            )

    def package_list(
        self,
        project_suuid: str,
        limit: int = 100,
        offset: int = 0,
        ordering: str = "-created",
    ) -> List[Package]:
        """Get a list of packages in a project

        Args:
            project_suuid (str): SUUID of the project to get the packages from
            limit (int): Number of results to return. Defaults to 100.
            offset (int): The initial index from which to return the results. Defaults to 0.
            ordering (str): The ordering of the results. Defaults to "-created".

        Returns:
            List[Package]: List of packages for the project in a Package dataclass
        """
        return PackageGateway().list(
            project_suuid=project_suuid,
            limit=limit,
            offset=offset,
            ordering=ordering,
        )
