from pathlib import Path
from typing import List, Optional, Union

from askanna.core.dataclasses.package import Package
from askanna.core.download import ChunkedDownload
from askanna.core.exceptions import GetError
from askanna.gateways.api_client import client

from .utils import ListResponse


class PackageListResponse(ListResponse):
    def __init__(self, data: dict):
        super().__init__(data)
        self.results: List[Package] = [Package.from_dict(package) for package in data["results"]]

    @property
    def packages(self):
        return self.results


class PackageGateway:
    """Management of packages in AskAnna
    This is the class which act as gateway to the API of AskAnna
    """

    def list(
        self,
        project_suuid: Optional[str] = None,
        workspace_suuid: Optional[str] = None,
        created_by_name: Optional[str] = None,
        created_by_suuid: Optional[str] = None,
        page_size: Optional[int] = None,
        cursor: Optional[str] = None,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
    ) -> PackageListResponse:
        """Get a list of packages

        Args:
            project_suuid (str, optional): Project SUUID to filter for packages in a project. Defaults to None.
            workspace_suuid (str, optional): Workspace SUUID to filter for packages in a workspace. Defaults to None.
            created_by_name (str, optional): Filter packages on a created by name. Defaults to None.
            created_by_suuid (str, optional): Filter packages on a created by SUUID. Defaults to None.
            page_size (int, optional): Number of packages to return per page. Defaults to the default value of
                the backend.
            cursor (str, optional): Cursor to start the page from. Defaults to None.
            order_by (str, optional): Order by field(s). Defaults to the default value of the backend.
            search (str, optional): Search for a specific package.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            PackageListResponse: The response from the API with a list of packages and pagination information
        """
        assert page_size is None or page_size > 0, "page_size must be a positive integer"

        response = client.get(
            url=client.askanna_url.package.package_list(),
            params={
                "project_suuid": project_suuid,
                "workspace_suuid": workspace_suuid,
                "created_by_name": created_by_name,
                "created_by_suuid": created_by_suuid,
                "page_size": page_size,
                "cursor": cursor,
                "order_by": order_by,
                "search": search,
            },
        )

        if response.status_code != 200:
            error_message = f"{response.status_code} - Something went wrong while retrieving package list"
            try:
                error_message += f":\n  {response.json()}"
            except ValueError:
                pass
            raise GetError(error_message)

        return PackageListResponse(response.json())

    def detail(self, package_suuid: str) -> Package:
        """Get information of a package

        Args:
            package_suuid (str): SUUID of the package

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Package: Package information in a Package dataclass
        """

        response = client.get(
            url=client.askanna_url.package.package_detail(package_suuid),
        )

        if response.status_code == 404:
            raise GetError(f"404 - The package SUUID '{package_suuid}' was not found")
        if response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving package SUUID '{package_suuid}': "
                f"{response.json()}"
            )

        return Package.from_dict(response.json())

    def download(self, package_suuid: str, output_path: Optional[Union[Path, str]] = None) -> Union[bytes, None]:
        """Download a package

        Args:
            package_suuid (str): SUUID of the package
            output_path (Path | str, optional): Path to save the package to. Defaults to None.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            bytes or None: The package as bytes or None if output_path is set
        """
        url = client.askanna_url.package.package_download(package_suuid)
        response = client.get(url)

        if response.status_code == 404:
            raise GetError(f"404 - Package SUUID '{package_suuid}' was not found")
        elif response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving the package SUUID '{package_suuid}': "
                + str(response.json())
            )

        download_url = response.json().get("target")

        if output_path:
            download = ChunkedDownload(download_url)

            if download.status_code == 404:
                raise GetError(f"404 - Package SUUID '{package_suuid}' was not found")
            if download.status_code != 200:
                raise GetError(
                    f"{download.status_code} - Something went wrong while retrieving the pacakage SUUID "
                    f"'{package_suuid}'"
                )

            download.download(output_path)
            return None
        else:
            response = client.get(download_url, stream=True)

            if response.status_code == 404:
                raise GetError(f"404 - Package SUUID '{package_suuid}' was not found")
            if response.status_code != 200:
                raise GetError(
                    f"{response.status_code} - Something went wrong while retrieving the package SUUID "
                    f"'{package_suuid}': {response.json()}"
                )

            return response.content
