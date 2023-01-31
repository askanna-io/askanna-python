from typing import List, Optional

from askanna.core.dataclasses.variable import Variable
from askanna.core.exceptions import DeleteError, GetError, PatchError, PostError
from askanna.gateways.api_client import client

from .utils import ListResponse


class VariableListResponse(ListResponse):
    def __init__(self, data: dict):
        super().__init__(data)
        self.results: List[Variable] = [Variable.from_dict(variable) for variable in data["results"]]

    @property
    def variables(self):
        return self.results


class VariableGateway:
    """Management of variables in AskAnna
    This is the class which act as gateway to the API of AskAnna
    """

    def list(
        self,
        project_suuid: Optional[str] = None,
        workspace_suuid: Optional[str] = None,
        is_masked: Optional[bool] = None,
        page_size: Optional[int] = None,
        cursor: Optional[str] = None,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
    ) -> VariableListResponse:
        """List variables with the option to filter and order options

        Args:
            project_suuid (str, optional): Project SUUID to filter for variables in a project. Defaults to None.
            workspace_suuid (str, optional): Workspace SUUID to filter for variables in a workspace. Defaults to None.
            is_masked (bool, optional): Filter on variables that are masked or not. Defaults to None.
            page_size (int, optional): Number of results per page. Defaults to the default value of the backend.
            cursor (str, optional): Cursor to start the page from. Defaults to None.
            order_by (str, optional): Order by field(s). Defaults to the default value of the backend.
            search (str, optional): Search for a specific variable.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            VariableListResponse: The response from the API with a list of variables and pagination information.
        """
        assert page_size is None or page_size > 0, "page_size must be a positive integer"
        assert is_masked is None or isinstance(is_masked, bool), "is_masked must be a boolean"

        response = client.get(
            url=client.askanna_url.variable.variable(),
            params={
                "project_suuid": project_suuid,
                "workspace_suuid": workspace_suuid,
                "is_masked": is_masked,
                "page_size": page_size,
                "cursor": cursor,
                "order_by": order_by,
                "search": search,
            },
        )

        if response.status_code != 200:
            error_message = response.json().get("detail", "Something went wrong while retrieving variable list")
            try:
                error_message += f": {response.json()}"
            except ValueError:
                pass
            raise GetError(error_message)

        return VariableListResponse(response.json())

    def detail(self, variable_suuid: str) -> Variable:
        """Get the details of a variable

        Args:
            variable_suuid (str): SUUID of the variable

        Returns:
            Variable: A variable dataclass
        """
        response = client.get(url=client.askanna_url.variable.variable_detail(variable_suuid))
        if response.status_code == 404:
            raise GetError(f"{response.status_code} - The variable SUUID '{variable_suuid}' was not found")
        if response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving the variable SUUID "
                f"'{variable_suuid}': {response.json()}"
            )

        return Variable.from_dict(response.json())

    def create(self, project_suuid: str, name: str, value: str, is_masked: bool = False) -> Variable:
        """Create a new variable for a project

        Args:
            project_suuid (str): SUUID of the project
            name (str): Name of the variable
            value (str): Value of the variable
            is_masked (bool, optional): Whether the value should be masked or not. Defaults to False.

        Raises:
            PostError: Error based on response status code with the error message from the API

        Returns:
            Variable: A variable dataclass of the newly created variable
        """
        assert isinstance(is_masked, bool), "is_masked must be a boolean"

        response = client.create(
            url=client.askanna_url.variable.variable(),
            json={
                "name": name,
                "value": value,
                "is_masked": is_masked,
                "project_suuid": project_suuid,
            },
        )

        if response.status_code != 201:
            raise PostError(
                f"{response.status_code} - Something went wrong while creating the variable: {response.json()}"
            )

        return Variable.from_dict(response.json())

    def change(
        self,
        variable_suuid: str,
        name: Optional[str] = None,
        value: Optional[str] = None,
        is_masked: Optional[bool] = None,
    ) -> Variable:
        """Change the name, value or is_masked of a variable

        Note: is_masked can only be changed to True, a masked variable cannot be set to unmasked.

        Args:
            variable_suuid (str): SUUID of the variable to change
            name (str, optional): New name of the variable. Defaults to None.
            value (str, optional): New value of the variable. Defaults to None.
            is_masked (bool, optional): New is_masked value of the variable. Defaults to None.

        Raises:
            ValueError: Error if none of the arguments 'name', 'value' or 'is_masked' are provided.
            PatchError: Error based on response status code with the error message from the API

        Returns:
            Variable: The updated variable in a Variable dataclass
        """
        changes = {}
        if name:
            changes.update({"name": name})
        if value:
            changes.update({"value": value})
        if is_masked:
            assert isinstance(is_masked, bool), "is_masked must be a boolean"
            changes.update({"is_masked": is_masked})

        if not changes:
            raise ValueError("At least one of the arguments 'name', 'value' or 'is_masked' should be provided.")

        response = client.patch(
            url=client.askanna_url.variable.variable_detail(variable_suuid),
            json=changes,
        )

        if response.status_code == 404:
            raise PatchError(f"{response.status_code} - The variable SUUID '{variable_suuid}' was not found")
        if response.status_code != 200:
            raise PatchError(
                f"{response.status_code} - Something went wrong while updating the variable SUUID '{variable_suuid}': "
                f"{response.json()}"
            )

        return Variable.from_dict(response.json())

    def delete(self, variable_suuid: str) -> bool:
        """Delete a variable

        Args:
            variable_suuid (str): SUUID of the variable

        Raises:
            DeleteError: Error based on response status code with the error message from the API

        Returns:
            bool: True if the variable was succesfully deleted
        """
        response = client.delete(
            url=client.askanna_url.variable.variable_detail(variable_suuid),
        )

        if response.status_code == 404:
            raise DeleteError(f"{response.status_code} - The variable SUUID '{variable_suuid}' was not found")
        if response.status_code != 204:
            raise DeleteError(
                f"{response.status_code} - Something went wrong while deleting the variable SUUID '{variable_suuid}': "
                f"{response.json()}"
            )

        return True
