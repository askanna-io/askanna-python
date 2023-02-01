from pathlib import Path
from typing import List, Optional, Union

from askanna.core.dataclasses.package import Package
from askanna.gateways.package import PackageGateway

from .mixins import ListMixin

__all__ = [
    "PackageSDK",
]


class PackageSDK(ListMixin):
    """Management of packages in AskAnna
    This class is a wrapper around the PackageGateway and can be used to manage packages in Python.
    """

    gateway = PackageGateway()
    package_suuid = None

    def _get_package_suuid(self) -> str:
        if not self.package_suuid:
            raise ValueError("No package SUUID set")

        return self.package_suuid

    def list(
        self,
        project_suuid: Optional[str] = None,
        workspace_suuid: Optional[str] = None,
        created_by_name: Optional[str] = None,
        created_by_suuid: Optional[str] = None,
        number_of_results: int = 100,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Package]:
        """List all packages with filter and order options

        Args:
            project_suuid (str, optional): Project SUUID to filter for packages in a project. Defaults to None.
            workspace_suuid (str, optional): Workspace SUUID to filter for packages in a workspace. Defaults to None.
            created_by_name (str, optional): Filter packages on a created by name. Defaults to None.
            created_by_suuid (str, optional): Filter packages on a created by SUUID. Defaults to None.
            page_size (int, optional): Number of packages to return per page. Defaults to the default value of
                the backend.
            number_of_results (int): Number of packages to return. Defaults to 100.
            order_by (str, optional): Order by field(s).
            search (str, optional): Search for a specific package.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            List[Package]: A list of packages. List items are of type Package dataclass.
        """
        return super().list(
            number_of_results=number_of_results,
            order_by=order_by,
            other_query_params={
                "project_suuid": project_suuid,
                "workspace_suuid": workspace_suuid,
                "created_by_name": created_by_name,
                "created_by_suuid": created_by_suuid,
                "search": search,
            },
        )

    def info(self, package_suuid: Optional[str] = None) -> Package:
        """Get information of a package

        Args:
            package_suuid (str): SUUID of the package

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Package: Package information in a Package dataclass
        """
        if package_suuid:
            self.package_suuid = package_suuid

        return self.gateway.detail(self._get_package_suuid())

    def get(self, package_suuid: Optional[str] = None) -> Union[bytes, None]:
        """Get the content of a package

        Args:
            package_suuid (str): SUUID of the package

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            bytes or None: The package in bytes
        """
        if package_suuid:
            self.package_suuid = package_suuid
        return self.gateway.download(self._get_package_suuid())

    def download(
        self,
        output_path: Union[Path, str],
        package_suuid: Optional[str] = None,
    ) -> None:
        """Download the content of a package and save it to output_path

        Args:
            output_path (Path | str): Path to download the package to
            package_suuid (str): SUUID of the package

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            bytes or None: The package in bytes, or None if output_path is set
        """
        if package_suuid:
            self.package_suuid = package_suuid

        self.gateway.download(self._get_package_suuid(), output_path)
