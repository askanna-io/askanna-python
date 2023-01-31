from typing import List, Optional

from askanna.core.dataclasses.variable import Variable
from askanna.gateways.variable import VariableGateway

from .mixins import ListMixin

__all__ = [
    "VariableSDK",
]


class VariableSDK(ListMixin):
    """Management of variables in AskAnna
    This class is a wrapper around the VariableGateway and can be used to manage variables in Python.
    """

    gateway = VariableGateway()

    def list(
        self,
        project_suuid: Optional[str] = None,
        workspace_suuid: Optional[str] = None,
        is_masked: Optional[bool] = None,
        number_of_results: int = 100,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Variable]:
        """List variables with filter and order options

        Args:
            project_suuid (str, optional): SUUID of the project to filter on. Defaults to None.
            workspace_suuid (str, optional): SUUID of the workspace to filter on. Defaults to None.
            is_masked (bool, optional): Filter on masked variables. Defaults to None.
            number_of_results (int, optional): Number of results to return. Defaults to 100.
            order_by (str, optional): Order by a specific field. Defaults to None.
            search (str, optional): Search for a specific variable. Defaults to None.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            List[Variable]: List of variables. List items are of type Variable dataclass
        """
        return super().list(
            number_of_results=number_of_results,
            order_by=order_by,
            other_query_params={
                "project_suuid": project_suuid,
                "workspace_suuid": workspace_suuid,
                "is_masked": is_masked,
                "search": search,
            },
        )

    def get(self, variable_suuid: str) -> Variable:
        """Get information of a variable

        Args:
            variable_suuid (str): SUUID of the variable

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Variable: Variable info in a Variable dataclass
        """
        return self.gateway.detail(variable_suuid=variable_suuid)

    def add(self, project_suuid: str, name: str, value: str, is_masked: bool = False) -> Variable:
        """Add a new variable to a project

        Args:
            project_suuid (str): SUUID of the project
            name (str): Name of the variable
            value (str): Value of the variable
            is_masked (bool, optional): Mask the variable. Defaults to False.

        Raises:
            PostError: Error based on response status code with the error message from the API

        Returns:
            Variable: The newly created variable in a Variable dataclass
        """
        return self.gateway.create(
            project_suuid=project_suuid,
            name=name,
            value=value,
            is_masked=is_masked,
        )

    def change(
        self,
        variable_suuid: str,
        name: Optional[str] = None,
        value: Optional[str] = None,
        is_masked: Optional[bool] = None,
    ) -> Variable:
        """Change the name, value and/or mask of a variable

        Note: is_masked can only be changed to True, a masked variable cannot be set to unmasked.

        Args:
            variable_suuid (str): SUUID of the variable
            name (str, optional): Name of the variable. Defaults to None.
            value (str, optional): Value of the variable. Defaults to None.
            is_masked (bool, optional): Mask the variable. Defaults to None.

        Raises:
            PatchError: Error based on response status code with the error message from the API

        Returns:
            Variable: The updated variable in a Variable dataclass
        """
        return self.gateway.change(
            variable_suuid=variable_suuid,
            name=name,
            value=value,
            is_masked=is_masked,
        )

    def delete(self, variable_suuid: str) -> bool:
        """Delete a variable

        Args:
            variable_suuid (str): SUUID of the variable

        Raises:
            DeleteError: Error based on response status code with the error message from the API

        Returns:
            bool: True if the variable was successfully deleted
        """
        return self.gateway.delete(variable_suuid=variable_suuid)
