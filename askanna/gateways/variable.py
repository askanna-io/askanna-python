from typing import List, Optional

from askanna.core.dataclasses.project import Variable
from askanna.core.exceptions import DeleteError, GetError, PatchError, PostError
from askanna.gateways.api_client import client


class VariableGateway:
    """Management of variables in AskAnna
    This is the class which act as gateway to the API of AskAnna
    """

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        project_suuid: Optional[str] = None,
        ordering: str = "-created",
    ) -> List[Variable]:
        """List variables with the option to filter on project

        Args:
            limit (int, optional): Number of results to return. Defaults to 100.
            offset (int, optional): The initial index from which to return the results. Defaults to 0.
            project_suuid (str, optional): Project SUUID to filter for variables in a project. Defaults to None.
            ordering (str, optional): Ordering of the results. Defaults to "-created".

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            List[Variable]: A list of variables. List items are of type Variable dataclass.
        """
        query = {
            "offset": offset,
            "limit": limit,
            "ordering": ordering,
        }
        if project_suuid:
            url = client.askanna_url.project.variable(project_suuid=project_suuid)
        else:
            url = client.askanna_url.variable.variable()

        r = client.get(url, params=query)

        if r.status_code != 200:
            raise GetError(f"{r.status_code} - Something went wrong while retrieving variables: {r.json()}")

        return [Variable.from_dict(variable) for variable in r.json().get("results")]

    def detail(self, variable_suuid: str) -> Variable:
        """Get the details of a variable

        Args:
            variable_suuid (str): SUUID of the variable

        Returns:
            Variable: A variable dataclass
        """
        url = client.askanna_url.variable.variable_detail(variable_suuid)
        r = client.get(url)
        return Variable(**r.json())

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
        url = client.askanna_url.variable.variable()
        r = client.create(
            url,
            json={
                "name": name,
                "value": value,
                "is_masked": is_masked,
                "project": project_suuid,
            },
        )
        if r.status_code == 201:
            return Variable(**r.json())
        else:
            raise PostError(f"{r.status_code} - Something went wrong while creating the variable: {r.json()}")

    def change(
        self,
        variable_suuid: str,
        name: Optional[str] = None,
        value: Optional[str] = None,
        is_masked: Optional[bool] = None,
    ) -> Variable:
        changes = {}
        if name:
            changes.update({"name": name})
        if value:
            changes.update({"value": value})
        if is_masked:
            changes.update({"is_masked": is_masked})

        if not changes:
            raise ValueError("At least one of the arguments 'name', 'value' or 'is_masked' should be provided.")

        url = client.askanna_url.variable.variable_detail(variable_suuid)
        r = client.patch(url, json=changes)

        if r.status_code == 200:
            return Variable(**r.json())
        if r.status_code == 404:
            raise PatchError(f"{r.status_code} - The variable SUUID '{variable_suuid}' was not found")

        raise PatchError(
            f"{r.status_code} - Something went wrong while updating the variable SUUID '{variable_suuid}': {r.json()}"
        )

    def delete(self, variable_suuid: str) -> bool:
        """Delete a variable

        Args:
            variable_suuid (str): SUUID of the variable

        Raises:
            DeleteError: Error based on response status code with the error message from the API

        Returns:
            bool: True if the variable was succesfully deleted
        """
        url = client.askanna_url.variable.variable_detail(variable_suuid)
        r = client.delete(url)

        if r.status_code == 204:
            return True
        if r.status_code == 404:
            raise DeleteError(f"{r.status_code} - The variable SUUID '{variable_suuid}' was not found")
        raise DeleteError(
            f"{r.status_code} - Something went wrong while deleting the variable SUUID '{variable_suuid}': {r.json()}"
        )
