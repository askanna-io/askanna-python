import warnings
from pathlib import Path
from typing import List, Optional, Union

from askanna.config import config
from askanna.core.dataclasses.job import Payload
from askanna.core.dataclasses.run import (
    ArtifactInfo,
    MetricList,
    Run,
    RunStatus,
    VariableList,
)
from askanna.core.exceptions import GetError
from askanna.gateways.run import RunGateway

from .job import JobSDK
from .mixins import ListMixin

__all__ = [
    "RunSDK",
    "GetRunsSDK",
]


class RunSDK(ListMixin):
    """Management of runs in AskAnna
    This class is a wrapper around the RunGateway and can be used to manage jobs in Python.
    """

    gateway = RunGateway()
    run_suuid = None

    def _get_run_suuid(self) -> str:
        if not self.run_suuid:
            raise ValueError("No run SUUID set")

        return self.run_suuid

    def list(
        self,
        run_suuid_list: Optional[List[str]] = None,
        job_name: Optional[str] = None,
        job_suuid: Optional[str] = None,
        project_suuid: Optional[str] = None,
        workspace_suuid: Optional[str] = None,
        include_metrics: bool = False,
        include_variables: bool = False,
        number_of_results: int = 100,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Run]:
        """List all runs with filter and order options

        Args:
            run_suuid_list (List[str], optional): List of run SUUIDs to filter on. Defaults to None.
            job_name (str, optional): Name of the job to filter on. Defaults to None.
            job_suuid (str, optional): SUUID of the job to filter on. Defaults to None.
            project_suuid (str, optional): SUUID of the project to filter on. Defaults to None.
            include_metrics (bool, optional): Include the metrics in the Run dataclass. Defaults to False.
            include_variables (bool, optional): Include the variables in the Run dataclass. Defaults to False.
            number_of_results (int): Number of runs to return. Defaults to 100.
            order_by (str, optional): Order by field(s).
            search (str, optional): Search for a specific run.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            List[Run]: List of runs. List items are of type Run dataclass.
        """

        if job_suuid and job_name:
            raise ValueError("Parameters 'job_suuid' and 'job_name' are both set. Please only set one.")
        if job_name:
            project_suuid = project_suuid or config.project.project_suuid
            job_suuid = JobSDK().get_job_by_name(job_name=job_name, project_suuid=project_suuid).suuid

        run_list = super().list(
            number_of_results=number_of_results,
            order_by=order_by,
            other_query_params={
                "run_suuid_list": run_suuid_list,
                "job_suuid": job_suuid,
                "project_suuid": project_suuid,
                "workspace_suuid": workspace_suuid,
                "search": search,
            },
        )

        if include_metrics:
            for run in run_list:
                run.metrics = self.gateway.metric(run.suuid)

        if include_variables:
            for run in run_list:
                run.variables = self.gateway.variable(run.suuid)

        return run_list

    def get(
        self,
        run_suuid: Optional[str] = None,
        include_metrics: bool = False,
        include_variables: bool = False,
    ) -> Run:
        """Get information about a run

        Args:
            run_suuid (str, optional): SUUID of the run
            include_metrics (bool, optional): Include the run metrics in the Run dataclass. Defaults to False.
            include_variables (bool, optional): Include the run variables in the Run dataclass. Defaults to False.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Run: Run info in a Run dataclass
        """
        run_suuid = run_suuid or self._get_run_suuid()
        run = self.gateway.detail(run_suuid)

        if include_metrics:
            run.metrics = self.gateway.metric(run.suuid)

        if include_variables:
            run.variables = self.gateway.variable(run.suuid)

        return run

    def change(
        self, run_suuid: Optional[str] = None, name: Optional[str] = None, description: Optional[str] = None
    ) -> Run:
        """Change the name or description of a run

        Args:
            run_suuid (str, optional): SUUID of the run
            name (str, optional): New name of the run. Defaults to None.
            description (str, optional): New description of the run. Defaults to None.

        Raises:
            PatchError: Error based on response status code with the error message from the API

        Returns:
            Run: The updated run in a Run dataclass
        """
        run_suuid = run_suuid or self._get_run_suuid()
        return self.gateway.change(run_suuid=run_suuid, name=name, description=description)

    def delete(self, run_suuid: Optional[str] = None) -> bool:
        """Delete a run

        Args:
            run_suuid (str, optional): SUUID of the run

        Raises:
            DeleteError: Error based on response status code with the error message from the API

        Returns:
            bool: True if the run was deleted
        """
        run_suuid = run_suuid or self._get_run_suuid()
        return self.gateway.delete(run_suuid=run_suuid)

    def start(
        self,
        job_suuid: Optional[str] = None,
        data: Optional[dict] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        project_suuid: Optional[str] = None,
        job_name: Optional[str] = None,
    ) -> RunStatus:
        """Start a run

        Args:
            job_suuid (str, optional): SUUID of the job to run. If not set, job_name must be set.
            data (dict, optional): Data to pass to the job. Defaults to None.
            name (str, optional): Name of the run. Defaults to None.
            description (str, optional): Description of the run. Defaults to None.
            project_suuid (str, optional): SUUID of the project to run the job in. Defaults to None.
            job_name (str, optional): Name of the job to run. Defaults to None.

        Raises:
            PostError: Error based on response status code with the error message from the API

        Returns:
            RunStatus: The run status information in a RunStatus dataclass
        """
        run_status = JobSDK().run_request(job_suuid, data, name, description, project_suuid, job_name)
        self.run_suuid = run_status.suuid
        return run_status

    def status(self, run_suuid: Optional[str] = None) -> RunStatus:
        """Get the status of a run

        Args:
            run_suuid (str, optional): SUUID of the run

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            RunStatus: The run status information in a RunStatus dataclass
        """
        run_suuid = run_suuid or self._get_run_suuid()
        return self.gateway.status(run_suuid)

    def log(self, run_suuid: Optional[str] = None, number_of_lines: int = 100) -> List:
        """Get the log of a run

        Args:
            run_suuid (str, optional): SUUID of the run
            number_of_lines (int, optional): Number of lines to return. Defaults to 100.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            List: List of log lines
        """
        run_suuid = run_suuid or self._get_run_suuid()
        return self.gateway.log(run_suuid, limit=number_of_lines)

    def get_metric(self, run_suuid: Optional[str] = None) -> MetricList:
        """Get the metrics of a run

        Args:
            run_suuid (str, optional): SUUID of the run

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            MetricList: List of metrics
        """
        run_suuid = run_suuid or self._get_run_suuid()
        return self.gateway.metric(run_suuid=run_suuid)

    def get_variable(self, run_suuid: Optional[str] = None) -> VariableList:
        """Get the variables used for a run

        Args:
            run_suuid (str, optional): SUUID of the run

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            VariableList: List of variables
        """
        run_suuid = run_suuid or self._get_run_suuid()
        return self.gateway.variable(run_suuid=run_suuid)

    def payload(
        self,
        run_suuid: Optional[str] = None,
        payload_suuid: Optional[str] = None,
        output_path: Optional[Union[Path, str]] = None,
    ) -> Union[bytes, None]:
        """Get the payload of a run
        Args:
            run_suuid (str, optional): SUUID of the run
            output_path (Path | str, optional): Path to save the payload to. Defaults to None.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            None: if output_path is set, the payload is saved to the output_path and None is returned
            bytes: if output_path is not set, the payload is returned as bytes
        """
        run_suuid = run_suuid or self._get_run_suuid()

        if not payload_suuid:
            payload_info = self.payload_info(run_suuid)

            if not payload_info:
                return

            payload_suuid = payload_info.suuid

        return self.gateway.payload(run_suuid=run_suuid, payload_suuid=payload_suuid, output_path=output_path)

    def payload_info(self, run_suuid: Optional[str] = None) -> Union[Payload, None]:
        """Get the payload info of a run

        Args:
            run_suuid (str, optional): SUUID of the run

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Payload: Payload info in a Payload dataclass
            None: If no payload is available for the run
        """
        run_suuid = run_suuid or self._get_run_suuid()
        return self.gateway.payload_info(run_suuid)

    def result(
        self, run_suuid: Optional[str] = None, output_path: Optional[Union[Path, str]] = None
    ) -> Union[bytes, None]:
        """Get the result of a run

        Args:
            run_suuid (str, optional): SUUID of the run
            output_path (Path | str, optional): Path to save the result to. Defaults to None.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            None: if output_path is set, the result is saved to the output_path and None is returned
            bytes: if output_path is not set, the result is returned as bytes
        """
        run_suuid = run_suuid or self._get_run_suuid()
        return self.gateway.result(run_suuid, output_path)

    def result_content_type(self, run_suuid: Optional[str] = None) -> str:
        """Get the content type of the result of a run

        Args:
            run_suuid (str, optional): SUUID of the run

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            str: Content type of the result
        """
        run_suuid = run_suuid or self._get_run_suuid()
        return self.gateway.result_content_type(run_suuid)

    def artifact(
        self, run_suuid: Optional[str] = None, output_path: Optional[Union[Path, str]] = None
    ) -> Union[bytes, None]:
        """Get the artifact of a run

        Args:
            run_suuid (str, optional): SUUID of the run
            output_path (Path | str, optional): Path to save the artifact to. Defaults to None.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            None: if output_path is set, the artifact is saved to the output_path and None is returned
            bytes: if output_path is not set, the artifact is returned as bytes
        """
        run_suuid = run_suuid or self._get_run_suuid()
        return self.gateway.artifact(run_suuid=run_suuid, output_path=output_path)

    def artifact_info(self, run_suuid: Optional[str] = None) -> ArtifactInfo:
        """Get the artifact info of a run

        Args:
            run_suuid (str, optional): SUUID of the run

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            ArtifactInfo: Artifact info in a ArtifactInfo dataclass
        """
        run_suuid = run_suuid or self._get_run_suuid()
        return self.gateway.artifact_info(run_suuid)


# TODO: remove the GetRunsSDK after release 0.21.0
class GetRunsSDK:
    """Get runs SDK"""

    def get(
        self,
        run_suuid_list: Optional[List[str]] = None,
        job_name: Optional[str] = None,
        job_suuid: Optional[str] = None,
        project_suuid: Optional[str] = None,
        workspace_suuid: Optional[str] = None,
        include_metrics: bool = False,
        include_variables: bool = False,
        number_of_results: int = 100,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Run]:
        """Get a list of runs

        Args:
            run_suuid_list (List[str], optional): List of run SUUIDs to filter on. Defaults to None.
            job_name (str, optional): Name of the job to filter on. Defaults to None.
            job_suuid (str, optional): SUUID of the job to filter on. Defaults to None.
            project_suuid (str, optional): SUUID of the project to filter on. Defaults to None.
            workspace_suuid (str, optional): SUUID of the workspace to filter on. Defaults to None.
            include_metrics (bool, optional): Include the metrics in the Run dataclass. Defaults to False.
            include_variables (bool, optional): Include the variables in the Run dataclass. Defaults to False.
            number_of_results (int): Number of runs to return. Defaults to 100.
            order_by (str, optional): Order by field(s).
            search (str, optional): Search for a specific run.

        Returns:
            List[Run]: List of runs. List items are of type Run dataclass.
        """
        warnings.warn("GetRunsSDK is deprecated, use RunSDK().list instead.", DeprecationWarning)
        return RunSDK().list(
            run_suuid_list=run_suuid_list,
            job_name=job_name,
            job_suuid=job_suuid,
            project_suuid=project_suuid,
            workspace_suuid=workspace_suuid,
            include_metrics=include_metrics,
            include_variables=include_variables,
            number_of_results=number_of_results,
            order_by=order_by,
            search=search,
        )


class ResultSDK:
    """Get result SDK"""

    def get(self, run_suuid: str) -> Union[bytes, None]:
        """Get the result of a run

        Args:
            run_suuid (str): SUUID of the run

        Returns:
            bytes: The result as bytes
            None: If the run has no result
        """
        return RunSDK().result(run_suuid)

    def download(self, run_suuid: str, output_path: Union[Path, str]) -> None:
        """Download the result of a run

        Args:
            run_suuid (str): SUUID of the run
            output_path (Path | str): Path to save the result to

        Returns:
            None
        """
        RunSDK().result(run_suuid, output_path)

    def get_content_type(self, run_suuid: str) -> str:
        """Get the content type of the result of a run

        Args:
            run_suuid (str): SUUID of the run

        Returns:
            str: Content type of the result
        """
        return RunSDK().result_content_type(run_suuid)

    def get_filename(self, run_suuid: str) -> str:
        """Get the filename of the result of a run

        Args:
            run_suuid (str): SUUID of the run

        Returns:
            str: Filename of the result
        """
        run = RunSDK().get(run_suuid)

        if run.result:
            return run.result.get("name", "")
        else:
            raise GetError(f"No result found for run SUUID '{run_suuid}'")


class ArtifactSDK:
    """Get artifact SDK"""

    def get(self, run_suuid: str) -> Union[bytes, None]:
        """Get the artifact of a run

        Args:
            run_suuid (str): SUUID of the run

        Returns:
            bytes: The artifact as bytes
            None: If the run has no artifact
        """
        return RunSDK().artifact(run_suuid)

    def download(self, run_suuid: str, output_path: Union[Path, str]) -> None:
        """Download the artifact of a run

        Args:
            run_suuid (str): SUUID of the run
            output_path (Path | str): Path to save the artifact to

        Returns:
            None
        """
        RunSDK().artifact(run_suuid, output_path)

    def info(self, run_suuid: str) -> ArtifactInfo:
        """Get the artifact info of a run

        Args:
            run_suuid (str): SUUID of the run

        Returns:
            ArtifactInfo: Artifact info in a ArtifactInfo dataclass
        """
        return RunSDK().artifact_info(run_suuid)
