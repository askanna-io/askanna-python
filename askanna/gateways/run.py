from pathlib import Path
from typing import List, Optional, Union

from askanna.core.dataclasses.job import Payload
from askanna.core.dataclasses.run import (
    ArtifactInfo,
    MetricList,
    MetricObject,
    Run,
    RunList,
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


class RunGateway:
    """Management of runs in AskAnna
    This is the class which act as the gateway to the API of AskAnna
    """

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        run_suuid_list: Optional[List[str]] = None,
        job_suuid: Optional[str] = None,
        project_suuid: Optional[str] = None,
        ordering: str = "-created",
    ) -> RunList:
        """List all runs with the option to filter on job

        Args:
            limit (int, optional): Number of results to return. Defaults to None (all workspaces).
            offset (int, optional): The initial index from which to return the results. Defaults to None.
            run_suuid_list (List[str], optional): List of run SUUIDs to filter on. Defaults to None.
            job_suuid (str, optional): Job SUUID to filter for runs in a job. Defaults to None.
            project_suuid (str, optional): Project SUUID to filter for runs in a project. Defaults to None.
            ordering (str, optional): Ordering of the results. Defaults to "-created".

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            RunList: List of runs in a RunList dataclass
        """
        query = {
            "offset": offset,
            "limit": limit,
            "ordering": ordering,
        }

        if job_suuid and not (run_suuid_list or project_suuid):
            url = client.askanna_url.job.run_list(job_suuid)
        else:
            url = client.askanna_url.run.run_list()

            if run_suuid_list and len(run_suuid_list) > 0:
                query.update({"runs": ",".join(run_suuid_list)})
            if job_suuid:
                query.update({"job": job_suuid})
            if project_suuid:
                query.update({"project": project_suuid})

        r = client.get(url, params=query)

        if r.status_code != 200:
            raise GetError(f"{r.status_code} - Something went wrong while retrieving runs: {r.json()}")

        return RunList(
            runs=[Run.from_dict(run) for run in r.json().get("results")],
        )

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
        r = client.get(url)

        if r.status_code == 200:
            return Run.from_dict(r.json())
        if r.status_code == 404:
            raise GetError(f"404 - The run SUUID '{run_suuid}' was not found")
        raise GetError(f"{r.status_code} - Something went wrong while retrieving run SUUID '{run_suuid}': {r.json()}")

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
        r = client.patch(url, json=changes)

        if r.status_code == 200:
            return Run.from_dict(r.json())
        if r.status_code == 404:
            raise PatchError(f"404 - The run SUUID '{run_suuid}' was not found")
        raise PatchError(
            f"{r.status_code} - Something went wrong while updating the run SUUID '{run_suuid}': {r.json()}"
        )

    def delete(self, run_suuid: str) -> bool:
        """Delete a run

        Args:
            run_suuid (str): SUUID of the run you want to delete

        Raises:
            DeleteError: Error based on response status code with the error message from the API

        Returns:
            bool: True if the run was succesfully deleted
        """
        url = client.askanna_url.job.job_detail(run_suuid)
        r = client.delete(url)

        if r.status_code == 204:
            return True
        if r.status_code == 404:
            raise DeleteError(f"404 - The job SUUID '{run_suuid}' was not found")
        raise DeleteError(
            f"{r.status_code} - Something went wrong while deleting the job SUUID '{run_suuid}': {r.json()}"
        )

    def status(self, run_suuid: str) -> RunStatus:
        """Get the status of a run

        Args:
            run_suuid (str): SUUID of the run you want to get the status of

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            RunStatus: The status of the run in a RunStatus dataclass
        """

        url = client.askanna_url.run.status(run_suuid)
        r = client.get(url)

        if r.status_code == 200:
            return RunStatus.from_dict(r.json())
        if r.status_code == 404:
            raise GetError(f"404 - The run SUUID '{run_suuid}' was not found")
        raise GetError(
            f"{r.status_code} - Something went wrong while retrieving the status of run SUUID '{run_suuid}': "
            f"{r.json()}"
        )

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
            r = client.get(url)

            if r.status_code == 200:
                return r.content
            if r.status_code == 404:
                raise GetError(f"404 - The manifest for run SUUID '{run_suuid}' was not found")

            raise GetError(
                f"{r.status_code} - Something went wrong while retrieving the manifest for run SUUID '{run_suuid}': "
                f"{r.json()}"
            )

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
        r = client.get(url)

        if r.status_code == 200:
            return MetricList(metrics=[MetricObject.from_dict(metric) for metric in r.json()])
        if r.status_code == 404:
            raise GetError(f"404 - The run SUUID '{run_suuid}' was not found")
        raise GetError(
            f"{r.status_code} - Something went wrong while retrieving the metrics of run SUUID '{run_suuid}': "
            f"{r.json()}"
        )

    def metric_update(self, run_suuid: str, metrics: MetricList) -> None:
        """Update the metrics of a run

        Args:
            run_suuid (str): SUUID of the run you want to update the metrics of
            metrics (MetricList): The list of metrics you want to save

        Raises:
            PutError: Error based on response status code with the error message from the API
        """
        url = client.askanna_url.run.metric_detail(run_suuid)
        r = client.put(url, json={"metrics": metrics.to_dict()})

        if r.status_code == 404:
            raise PutError(f"404 - The run SUUID '{run_suuid}' was not found")
        if r.status_code != 200:
            raise PutError(f"{r.status_code} - Something went wrong while updating metrics: {r.json()}")

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
        r = client.get(url)

        if r.status_code == 200:
            return VariableList(variables=[VariableObject.from_dict(variable) for variable in r.json()])
        if r.status_code == 404:
            raise GetError(f"404 - The run SUUID '{run_suuid}' was not found")
        raise GetError(
            f"{r.status_code} - Something went wrong while retrieving the variables of run SUUID '{run_suuid}': "
            f"{r.json()}"
        )

    def variable_update(self, run_suuid: str, variables: VariableList) -> None:
        """Update the variables of a run

        Args:
            run_suuid (str): SUUID of the run you want to update the variables of
            variables (VariableList): The list of variables you want to save

        Raises:
            PatchError: Error based on response status code with the error message from the API
        """
        url = client.askanna_url.run.variable_detail(run_suuid)
        r = client.patch(url, json={"variables": variables.to_dict()})

        if r.status_code == 404:
            raise PatchError(f"404 - The run SUUID '{run_suuid}' was not found")
        if r.status_code != 200:
            raise PatchError(f"{r.status_code} - Something went wrong while updating variables: {r.json()}")

    def log(self, run_suuid: str) -> List:
        """Get the log of a run

        Args:
            run_suuid (str): SUUID of the run you want to get the log of

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            log (List): The log of the run in a list
        """
        url = client.askanna_url.run.log(run_suuid)
        r = client.get(url)

        if r.status_code == 200:
            return list(r.json())
        if r.status_code == 404:
            raise GetError(f"404 - The run SUUID '{run_suuid}' was not found")
        raise GetError(
            f"{r.status_code} - Something went wrong while retrieving the log of run SUUID '{run_suuid}': {r.json()}"
        )

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
        r = client.get(url)

        if r.status_code == 404:
            raise GetError(f"404 - The run with run SUUID '{run_suuid}' was not found")
        elif r.status_code != 200:
            raise GetError(
                f"{r.status_code} - Something went wrong while retrieving the payload list of run SUUID "
                f"'{run_suuid}': {r.json()}"
            )

        # The payload list is a list of dicts, but we only want the first one because there could only be one payload
        # per run.
        if len(r.json()) > 0:
            return Payload.from_dict(r.json()[0])
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
        r = client.get(url)

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
            r = client.get(url)

            if r.status_code == 200:
                return r.content
            if r.status_code == 404:
                raise GetError(f"404 - The payload for run SUUID '{run_suuid}' was not found")

            raise GetError(
                f"{r.status_code} - Something went wrong while retrieving the payload for run SUUID '{run_suuid}': "
                f"{r.json()}"
            )

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
            r = client.get(url)

            if r.status_code == 200:
                return r.content
            if r.status_code == 404:
                raise GetError(f"404 - The result for run SUUID '{run_suuid}' was not found")

            raise GetError(
                f"{r.status_code} - Something went wrong while retrieving the result for run SUUID '{run_suuid}': "
                + str(r.json())
            )

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
        r = client.head(url)

        if r.status_code == 200:
            return str(r.headers.get("Content-Type"))
        if r.status_code == 404:
            raise HeadError(f"404 - The result for run SUUID '{run_suuid}' was not found")
        raise HeadError(
            f"{r.status_code} - Something went wrong while retrieving the result content type for run SUUID "
            f"'{run_suuid}': {r.json()}"
        )

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

        r = client.get(url)

        if r.status_code == 404:
            raise GetError(f"404 - The artifact for run SUUID '{run_suuid}' was not found")
        if r.status_code != 200:
            raise GetError(
                f"{r.status_code} - Something went wrong while retrieving the artifact for run SUUID '{run_suuid}': "
                + str(r.json())
            )

        download_url = r.json().get("target")

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
            r = client.get(download_url)

            if r.status_code == 200:
                return r.content
            if r.status_code == 404:
                raise GetError(f"404 - The artifact for run SUUID '{run_suuid}' was not found")

            raise GetError(
                f"{r.status_code} - Something went wrong while retrieving the artifact for run SUUID '{run_suuid}': "
                + str(r.json())
            )

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

        r = client.get(url)

        if r.status_code == 200:
            return ArtifactInfo.from_dict(r.json())
        if r.status_code == 404:
            raise GetError(f"404 - The artifact for run SUUID '{run_suuid}' was not found")
        raise GetError(
            f"{r.status_code} - Something went wrong while retrieving the artifact for run SUUID '{run_suuid}': "
            + str(r.json())
        )

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
        r = client.get(url)

        if r.status_code == 404 or len(r.json()) == 0:
            raise GetError(f"404 - The artifact for run SUUID '{run_suuid}' was not found")
        if r.status_code != 200:
            raise GetError(
                f"{r.status_code} - Something went wrong while retrieving the artifact for run SUUID '{run_suuid}': "
                + str(r.json())
            )

        return r.json()[0]["suuid"]
