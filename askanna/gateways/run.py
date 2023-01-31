from pathlib import Path
from typing import List, Optional, Union

from askanna.core.dataclasses.job import Payload
from askanna.core.dataclasses.run import (
    ArtifactInfo,
    MetricList,
    MetricObject,
    Run,
    RunStatus,
    VariableList,
    VariableObject,
)
from askanna.core.download import ChunkedDownload
from askanna.core.exceptions import (
    DeleteError,
    GetError,
    HeadError,
    PatchError,
    PutError,
)
from askanna.gateways.api_client import client

from .utils import ListResponse


class RunListResponse(ListResponse):
    def __init__(self, data: dict):
        super().__init__(data)
        self.results: List[Run] = [Run.from_dict(run) for run in data["results"]]

    @property
    def runs(self):
        return self.results


class RunGateway:
    """Management of runs in AskAnna
    This is the class which act as the gateway to the API of AskAnna
    """

    def list(
        self,
        run_suuid_list: Optional[List[str]] = None,
        job_suuid: Optional[str] = None,
        project_suuid: Optional[str] = None,
        workspace_suuid: Optional[str] = None,
        page_size: Optional[int] = None,
        cursor: Optional[str] = None,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
    ) -> RunListResponse:
        """List all runs with filter and order options

        Args:
            run_suuid_list (List[str], optional): List of run SUUIDs to filter on. Defaults to None.
            job_suuid (str, optional): Job SUUID to filter for runs in a job. Defaults to None.
            project_suuid (str, optional): Project SUUID to filter for runs in a project. Defaults to None.
            workspace_suuid (str, optional): Workspace SUUID to filter for runs in a workspace. Defaults to None.
            page_size (int, optional): Number of results per page. Defaults to the default value of the backend.
            cursor (str, optional): Cursor to start the page from. Defaults to None.
            order_by (str, optional): Order by a field. Defaults to None.
            search (str, optional): Search for a specific run. Defaults to None.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            RunListResponse: The response from the API with a list of runs and pagination information
        """
        assert page_size is None or page_size > 0, "page_size must be a positive integer"

        run_suuid = None
        if run_suuid_list and len(run_suuid_list) > 0:
            run_suuid = ",".join(run_suuid_list)

        response = client.get(
            url=client.askanna_url.run.run_list(),
            params={
                "run_suuid": run_suuid,
                "job_suuid": job_suuid,
                "project_suuid": project_suuid,
                "workspace_suuid": workspace_suuid,
                "page_size": page_size,
                "cursor": cursor,
                "order_by": order_by,
                "search": search,
            },
        )

        if response.status_code != 200:
            error_message = f"{response.status_code} - Something went wrong while retrieving the run list"
            try:
                error_message += f":\n  {response.json()}"
            except ValueError:
                pass
            raise GetError(error_message)

        return RunListResponse(response.json())

    def detail(self, run_suuid: str) -> Run:
        """Get information of a run

        Args:
            suuid (str): SUUID of the run

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Run: Run information in a Run dataclass
        """
        url = client.askanna_url.run.run_detail(run_suuid)
        response = client.get(url)

        if response.status_code == 404:
            raise GetError(f"404 - The run SUUID '{run_suuid}' was not found")
        if response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving run SUUID '{run_suuid}': "
                f"{response.json()}"
            )

        return Run.from_dict(response.json())

    def change(self, run_suuid: str, name: Optional[str] = None, description: Optional[str] = None) -> Run:
        """Change the name and/or description of a run

        Args:
            run_suuid (str): SUUID of the run you want to change the information of
            name (str, optional): New name for the run. Defaults to None.
            description (str, optional): New description of the run. Defaults to None.

        Raises:
            ValueError: Error if none of the arguments 'name' or 'description' are provided
            PatchError: Error based on response status code with the error message from the API

        Returns:
            Run: The changed run information in a Run dataclass
        """
        changes = {}
        if name:
            changes.update({"name": name})
        if description:
            changes.update({"description": description})

        if not changes:
            raise ValueError("At least one of the parameters 'name' or 'description' must be set.")

        url = client.askanna_url.run.run_detail(run_suuid)
        response = client.patch(url, json=changes)

        if response.status_code == 404:
            raise PatchError(f"404 - The run SUUID '{run_suuid}' was not found")
        if response.status_code != 200:
            raise PatchError(
                f"{response.status_code} - Something went wrong while updating the run SUUID '{run_suuid}': "
                f"{response.json()}"
            )

        return Run.from_dict(response.json())

    def delete(self, run_suuid: str) -> bool:
        """Delete a run

        Args:
            run_suuid (str): SUUID of the run you want to delete

        Raises:
            DeleteError: Error based on response status code with the error message from the API

        Returns:
            bool: True if the run was succesfully deleted
        """
        response = client.delete(
            url=client.askanna_url.run.run_detail(run_suuid),
        )

        if response.status_code == 404:
            raise DeleteError(f"404 - The job SUUID '{run_suuid}' was not found")
        if response.status_code != 204:
            raise DeleteError(
                f"{response.status_code} - Something went wrong while deleting the job SUUID '{run_suuid}': "
                f"{response.json()}"
            )

        return True

    def status(self, run_suuid: str) -> RunStatus:
        """Get the status of a run

        Args:
            run_suuid (str): SUUID of the run you want to get the status of

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            RunStatus: The status of the run in a RunStatus dataclass
        """
        response = client.get(
            url=client.askanna_url.run.status(run_suuid),
        )

        if response.status_code == 404:
            raise GetError(f"404 - The run SUUID '{run_suuid}' was not found")
        if response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving the status of run SUUID "
                f"'{run_suuid}': {response.json()}"
            )

        return RunStatus.from_dict(response.json())

    def manifest(
        self,
        run_suuid: str,
        output_path: Optional[Union[Path, str]] = None,
        overwrite: bool = False,
    ) -> Union[bytes, None]:
        """Get the manifest of a run and optionally save it to a file

        Args:
            run_suuid (str): SUUID of the run you want to get the manifest of
            output_path (Path | str, optional): Path to save the manifest to. Defaults to None.
            overwrite (bool, optional): Overwrite a file if it already exists. Defaults to False.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            bytes: The manifest of the run
        """
        url = client.askanna_url.run.manifest(run_suuid)

        if output_path:
            download = ChunkedDownload(url)

            if download.status_code == 404:
                raise GetError(f"404 - The manifest for run SUUID '{run_suuid}' was not found")
            if download.status_code != 200:
                raise GetError(
                    f"{download.status_code} - Something went wrong while retrieving the manifest for run SUUID "
                    f"'{run_suuid}'"
                )

            download.download(output_file=output_path, overwrite=overwrite)
            return None

        else:
            response = client.get(url)

            if response.status_code == 404:
                raise GetError(f"404 - The manifest for run SUUID '{run_suuid}' was not found")
            if response.status_code != 200:
                raise GetError(
                    f"{response.status_code} - Something went wrong while retrieving the manifest for run SUUID "
                    f"'{run_suuid}': {response.json()}"
                )

            return response.content

    def metric(self, run_suuid: str) -> MetricList:
        """Get the metrics of a run

        Args:
            run_suuid (str): SUUID of the run you want to get the metrics of

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            MetricList: The metrics of the run in a MetricList dataclass
        """
        url = client.askanna_url.run.metric(run_suuid)
        response = client.get(url)

        if response.status_code == 404:
            raise GetError(f"404 - The run SUUID '{run_suuid}' was not found")
        if response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving the metrics of run SUUID "
                f"'{run_suuid}': {response.json()}"
            )

        return MetricList(metrics=[MetricObject.from_dict(metric) for metric in response.json()["results"]])

    def metric_update(self, run_suuid: str, metrics: MetricList) -> None:
        """Update the metrics of a run

        Args:
            run_suuid (str): SUUID of the run you want to update the metrics of
            metrics (MetricList): The list of metrics you want to save

        Raises:
            PutError: Error based on response status code with the error message from the API
        """
        url = client.askanna_url.run.metric_detail(run_suuid)
        response = client.put(url, json={"metrics": metrics.to_dict()})

        if response.status_code == 404:
            raise PutError(f"404 - The run SUUID '{run_suuid}' was not found")
        if response.status_code != 200:
            raise PutError(f"{response.status_code} - Something went wrong while updating metrics: {response.json()}")

    def variable(self, run_suuid: str) -> VariableList:
        """Get the variables of a run

        Args:
            run_suuid (str): SUUID of the run you want to get the variables of

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            VariableList: The variables of the run in a VariableList dataclass
        """
        url = client.askanna_url.run.variable(run_suuid)
        response = client.get(url)

        if response.status_code == 404:
            raise GetError(f"404 - The run SUUID '{run_suuid}' was not found")
        if response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving the variables of run SUUID "
                f"'{run_suuid}': {response.json()}"
            )

        return VariableList(variables=[VariableObject.from_dict(variable) for variable in response.json()["results"]])

    def variable_update(self, run_suuid: str, variables: VariableList) -> None:
        """Update the variables of a run

        Args:
            run_suuid (str): SUUID of the run you want to update the variables of
            variables (VariableList): The list of variables you want to save

        Raises:
            PatchError: Error based on response status code with the error message from the API
        """
        url = client.askanna_url.run.variable_detail(run_suuid)
        response = client.patch(url, json={"variables": variables.to_dict()})

        if response.status_code == 404:
            raise PatchError(f"404 - The run SUUID '{run_suuid}' was not found")
        if response.status_code != 200:
            raise PatchError(
                f"{response.status_code} - Something went wrong while updating variables: {response.json()}"
            )

    def log(self, run_suuid: str, limit: Optional[int] = -1, offset: Optional[int] = None) -> List:
        """Get the log of a run

        Args:
            run_suuid (str): SUUID of the run you want to get the log of.
            limit (int, optional): Limit the number of log lines. Defaults to -1 (all log lines).
            offset (int, optional): Offset the number of log lines. Defaults to None.

        Raises:
            GetError: Error based on response status code with the error message from the API.

        Returns:
            log (List): The log of the run in a list. Each record is a list with 3 items: index, datetime and log line.
        """
        response = client.get(
            url=client.askanna_url.run.log(run_suuid),
            params={
                "limit": limit,
                "offset": offset,
            },
        )

        if response.status_code == 404:
            raise GetError(f"404 - The run SUUID '{run_suuid}' was not found")
        if response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving the log of run SUUID '{run_suuid}': "
                f"{response.json()}"
            )

        return list(response.json().get("results", []))

    def payload_info(self, run_suuid: str) -> Union[Payload, None]:
        """Get the payload info of a run

        Args:
            run_suuid (str): SUUID of the run you want to get the payload info of

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Payload or None: The payload info of the run in a Payload dataclass, or None in case there is no payload
        """
        url = client.askanna_url.run.payload_list(run_suuid)
        response = client.get(url)

        if response.status_code == 404:
            raise GetError(f"404 - The run with run SUUID '{run_suuid}' was not found")
        elif response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving the payload list of run SUUID "
                f"'{run_suuid}': {response.json()}"
            )

        # The payload list is a list of dicts, but we only want the first one because there could only be one payload
        # per run.
        if len(response.json()) > 0:
            return Payload.from_dict(response.json()[0])
        else:
            return None

    def payload(
        self, run_suuid: str, payload_suuid: str, output_path: Optional[Union[Path, str]] = None
    ) -> Union[bytes, None]:
        """Get the payload of a run and optionally save it to a file

        Args:
            run_suuid (str): SUUID of the run you want to get the payload content of
            payload_suuid (str): SUUID of the payload you want to get the content of
            output_path (Path | str, optional): Path to save the payload to. Defaults to None.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            bytes or None: The payload of the run in bytes, or None if output_path is set
        """
        url = client.askanna_url.run.payload_download(run_suuid, payload_suuid)

        if output_path:
            download = ChunkedDownload(url)

            if download.status_code == 404:
                raise GetError(f"404 - The payload for run SUUID '{run_suuid}' was not found")
            if download.status_code != 200:
                raise GetError(
                    f"{download.status_code} - Something went wrong while retrieving the payload for run SUUID "
                    f"'{run_suuid}'"
                )

            download.download(output_path)
            return None

        else:
            response = client.get(url)

            if response.status_code == 404:
                raise GetError(f"404 - The payload for run SUUID '{run_suuid}' was not found")
            if response.status_code != 200:
                raise GetError(
                    f"{response.status_code} - Something went wrong while retrieving the payload for run SUUID "
                    f"'{run_suuid}': {response.json()}"
                )

            return response.content

    def result(self, run_suuid: str, output_path: Optional[Union[Path, str]] = None) -> Union[bytes, None]:
        """Get the result of a run and optionally save it to a file

        Args:
            run_suuid (str): SUUID of the run you want to get the result of
            output_path (Path | str, optional): Path to save the result to. Defaults to None.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            bytes or None: The result of the run in bytes, or None if output_path is set
        """
        url = client.askanna_url.run.result(run_suuid)

        if output_path:
            download = ChunkedDownload(url)

            if download.status_code == 404:
                raise GetError(f"404 - The result for run SUUID '{run_suuid}' was not found")
            if download.status_code != 200:
                raise GetError(
                    f"{download.status_code} - Something went wrong while retrieving the result for run SUUID "
                    f"'{run_suuid}'"
                )

            download.download(output_path)
            return None

        else:
            response = client.get(url)

            if response.status_code == 404:
                raise GetError(f"404 - The result for run SUUID '{run_suuid}' was not found")
            if response.status_code != 200:
                raise GetError(
                    f"{response.status_code} - Something went wrong while retrieving the result for run SUUID "
                    f"'{run_suuid}': {response.json()}"
                )

            return response.content

    def result_content_type(self, run_suuid: str) -> str:
        """Get the content type of the result of a run

        Args:
            run_suuid (str): SUUID of the run you want to get the result content type of

        Raises:
            HeadError: Error based on response status code with the error message from the API

        Returns:
            str: The content type of the result of the run
        """

        url = client.askanna_url.run.result(run_suuid)
        response = client.head(url)

        if response.status_code == 404:
            raise HeadError(f"404 - The result for run SUUID '{run_suuid}' was not found")
        if response.status_code != 200:
            raise HeadError(
                f"{response.status_code} - Something went wrong while retrieving the result content type for run "
                f"SUUID '{run_suuid}': {response.json()}"
            )

        return str(response.headers.get("Content-Type"))

    def artifact(
        self,
        run_suuid: str,
        artifact_suuid: Optional[str] = None,
        output_path: Optional[Union[Path, str]] = None,
    ) -> Union[bytes, None]:
        """Get the artifact of a run and optionally save it to a file

        Args:
            run_suuid (str): SUUID of the run you want to get the artifact of
            output_path (Path | str, optional): Path to save the artifact to. Defaults to None.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            bytes or None: The artifact of the run in bytes, or None if output_path is set
        """
        artifact_suuid = artifact_suuid or self._get_artifact_suuid(run_suuid)
        url = client.askanna_url.run.artifact_download(run_suuid, artifact_suuid)

        response = client.get(url)

        if response.status_code == 404:
            raise GetError(f"404 - The artifact for run SUUID '{run_suuid}' was not found")
        if response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving the artifact for run SUUID "
                f"'{run_suuid}': {response.json()}"
            )

        download_url = response.json().get("target")

        if output_path:
            download = ChunkedDownload(download_url)

            if download.status_code == 404:
                raise GetError(f"404 - The artifact for run SUUID '{run_suuid}' was not found")
            if download.status_code != 200:
                raise GetError(
                    f"{download.status_code} - Something went wrong while retrieving the artifact for run SUUID "
                    f"'{run_suuid}'"
                )

            download.download(output_path)
            return None

        else:
            response = client.get(download_url)

            if response.status_code == 404:
                raise GetError(f"404 - The artifact for run SUUID '{run_suuid}' was not found")
            if response.status_code != 200:
                raise GetError(
                    f"{response.status_code} - Something went wrong while retrieving the artifact for run SUUID "
                    f"'{run_suuid}': {response.json()}"
                )

            return response.content

    def artifact_info(self, run_suuid: str, artifact_suuid: Optional[str] = None) -> ArtifactInfo:
        """Get artifact info of a run

        Args:
            run_suuid (str): SUUID of the run you want to get the artifact of
            artifact_suuid (str, optional): SUUID of the artifact you want to get the info of. Defaults to None.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            ArtifactInfo: Info about the artifact of a run in a ArtifactInfo dataclass
        """
        artifact_suuid = artifact_suuid or self._get_artifact_suuid(run_suuid)
        url = client.askanna_url.run.artifact_detail(run_suuid, artifact_suuid)

        response = client.get(url)

        if response.status_code == 404:
            raise GetError(f"404 - The artifact for run SUUID '{run_suuid}' was not found")
        if response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving the artifact for run SUUID "
                f"'{run_suuid}': {response.json()}"
            )

        return ArtifactInfo.from_dict(response.json())

    def _get_artifact_suuid(self, run_suuid: str) -> str:
        """Get the artifact SUUID of the artifact of a run

        Args:
            run_suuid (str): SUUID of the run you want to get the artifact SUUID of

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            str: SUUID of the artifact of the run
        """
        url = client.askanna_url.run.artifact_list(run_suuid)
        response = client.get(url)

        if response.status_code == 404 or len(response.json()) == 0:
            raise GetError(f"404 - The artifact for run SUUID '{run_suuid}' was not found")
        if response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving the artifact for run SUUID "
                f"'{run_suuid}': {response.json()}"
            )

        return response.json()[0]["suuid"]
