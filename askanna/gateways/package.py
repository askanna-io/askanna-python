from pathlib import Path
from typing import List, Optional, Union

from askanna.core.dataclasses.package import Package
from askanna.core.download import ChunkedDownload
from askanna.core.exceptions import GetError
from askanna.gateways.api_client import client


class PackageGateway:
    """Management of packages in AskAnna
    This is the class which act as gateway to the API of AskAnna
    """

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        project_suuid: Optional[str] = None,
        ordering: str = "-created",
    ) -> List[Package]:
        """Get a list of packages

        Args:
            limit (int): Number of results to return. Defaults to 100.
            offset (int): The initial index from which to return the results. Defaults to 0.
            project_suuid (str, optional): Project SUUID to filter for packages in a project. Defaults to None.
            ordering (str): Ordering of the results. Defaults to "-created".

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            List[Package]: A list of packages. List items are of type Package dataclass.
        """
        query = {
            "offset": offset,
            "limit": limit,
            "ordering": ordering,
        }

        if project_suuid:
            url = client.askanna_url.project.package_list(project_suuid)
        else:
            url = client.askanna_url.package.package_list()

        r = client.get(url, params=query)

        if r.status_code != 200:
            raise GetError(f"{r.status_code} - Something went wrong while retrieving packages: {r.json()}")

        return [Package(**package) for package in r.json().get("results")]

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
        r = client.get(url)

        if r.status_code == 404:
            raise GetError(f"404 - Package SUUID '{package_suuid}' was not found")
        elif r.status_code != 200:
            raise GetError(
                f"{r.status_code} - Something went wrong while retrieving the package SUUID '{package_suuid}': "
                + str(r.json())
            )

        download_url = r.json().get("target")

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
            r = client.get(download_url, stream=True)

            if r.status_code == 200:
                return r.content
            if r.status_code == 404:
                raise GetError(f"404 - Package SUUID '{package_suuid}' was not found")

            raise GetError(
                f"{r.status_code} - Something went wrong while retrieving the package SUUID '{package_suuid}': "
                + str(r.json())
            )
