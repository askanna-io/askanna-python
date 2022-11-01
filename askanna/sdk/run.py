from pathlib import Path
from typing import List, Optional, Union

from askanna.config import config
from askanna.core.dataclasses.run import ArtifactInfo, Payload, Run, RunList, RunStatus
from askanna.core.exceptions import GetError
from askanna.gateways.job import JobGateway
from askanna.gateways.run import RunGateway

__all__ = [
    "RunSDK",
    "GetRunsSDK",
]


class RunSDK:
    def __init__(self):
        self.run_suuid = None
        self.run_gateway = RunGateway()

    def _get_run_suuid(self) -> str:
        if not self.run_suuid:
            raise ValueError("No run SUUID set")

        return self.run_suuid

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        run_suuid_list: Optional[List[str]] = None,
        job_name: Optional[str] = None,
        job_suuid: Optional[str] = None,
        project_suuid: Optional[str] = None,
        include_metrics: bool = False,
        include_variables: bool = False,
        ordering: str = "-created",
    ) -> RunList:
        """Get a list of runs

        Args:
            limit (int, optional): Limit the number of runs in the result. Defaults to 100.
            offset (int, optional): Offset the number of runs in the result. Defaults to 0.
            run_suuid_list (List[str], optional): List of run SUUIDs to filter on. Defaults to None.
            job_name (str, optional): Name of the job to filter on. Defaults to None.
            job_suuid (str, optional): SUUID of the job to filter on. Defaults to None.
            project_suuid (str, optional): SUUID of the project to filter on. Defaults to None.
            include_metrics (bool, optional): Include the metrics in the Run dataclass. Defaults to False.
            include_variables (bool, optional): Include the variables in the Run dataclass. Defaults to False.
            ordering (str, optional): Ordering of the run list. Defaults to "-created".

        Returns:
            RunList: List of runs in a RunList dataclass
        """

        if job_suuid and job_name:
            raise ValueError("Parameters 'job_suuid' and 'job_name' are both set. Please only set one.")
        if job_name:
            project_suuid = project_suuid or config.project.project_suuid
            job_suuid = JobGateway().get_job_by_name(job_name=job_name, project_suuid=project_suuid).short_uuid

        run_list = self.run_gateway.list(
            limit=limit,
            offset=offset,
            run_suuid_list=run_suuid_list,
            job_suuid=job_suuid,
            project_suuid=project_suuid,
            ordering=ordering,
        )

        if include_metrics:
            for run in run_list:
                run.metrics = self.run_gateway.metric(run.short_uuid)

        if include_variables:
            for run in run_list:
                run.variables = self.run_gateway.variable(run.short_uuid)

        return run_list

    def get(
        self,
        run_suuid: Optional[str] = None,
        include_metrics: bool = False,
        include_variables: bool = False,
    ) -> Run:
        run_suuid = run_suuid or self._get_run_suuid()
        run = self.run_gateway.detail(run_suuid)

        if include_metrics:
            run.metrics = self.run_gateway.metric(run.short_uuid)

        if include_variables:
            run.variables = self.run_gateway.variable(run.short_uuid)

        return run

    def start(
        self,
        job_suuid: Optional[str] = None,
        data: Optional[dict] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        project_suuid: Optional[str] = None,
        job_name: Optional[str] = None,
    ) -> RunStatus:
        if not job_suuid and not job_name:
            raise ValueError("To start a run we need at least a job SUUID or job name")
        if job_suuid and job_name:
            raise ValueError("Parameters 'job_suuid' and 'job_name' are both set. Please only set one.")
        if job_name:
            project_suuid = project_suuid or config.project.project_suuid
            job_suuid = JobGateway().get_job_by_name(job_name=job_name, project_suuid=project_suuid).short_uuid
        if not job_suuid:
            raise ValueError("No job SUUID set")

        run_status = JobGateway().run_request(job_suuid, data, name, description)
        self.run_suuid = run_status.short_uuid
        return run_status

    def status(self, run_suuid: Optional[str] = None) -> RunStatus:
        run_suuid = run_suuid or self._get_run_suuid()
        return self.run_gateway.status(run_suuid)

    def log(self, run_suuid: Optional[str] = None) -> List:
        run_suuid = run_suuid or self._get_run_suuid()
        return self.run_gateway.log(run_suuid)

    def payload(
        self, run_suuid: Optional[str] = None, output_path: Optional[Union[Path, str]] = None
    ) -> Union[bytes, None]:
        run_suuid = run_suuid or self._get_run_suuid()
        payload_info = self.payload_info(run_suuid)

        if not payload_info:
            return

        return self.run_gateway.payload(
            run_suuid=run_suuid, payload_suuid=payload_info.short_uuid, output_path=output_path
        )

    def payload_info(self, run_suuid: Optional[str] = None) -> Union[Payload, None]:
        run_suuid = run_suuid or self._get_run_suuid()
        return self.run_gateway.payload_info(run_suuid)

    def result(
        self, run_suuid: Optional[str] = None, output_path: Optional[Union[Path, str]] = None
    ) -> Union[bytes, None]:
        run_suuid = run_suuid or self._get_run_suuid()
        return self.run_gateway.result(run_suuid, output_path)

    def result_content_type(self, run_suuid: Optional[str] = None) -> str:
        run_suuid = run_suuid or self._get_run_suuid()
        return self.run_gateway.result_content_type(run_suuid)

    def artifact(
        self, run_suuid: Optional[str] = None, output_path: Optional[Union[Path, str]] = None
    ) -> Union[bytes, None]:
        run_suuid = run_suuid or self._get_run_suuid()
        return self.run_gateway.artifact(run_suuid=run_suuid, output_path=output_path)

    def artifact_info(self, run_suuid: Optional[str] = None) -> ArtifactInfo:
        run_suuid = run_suuid or self._get_run_suuid()
        return self.run_gateway.artifact_info(run_suuid)


class GetRunsSDK:
    def get(
        self,
        limit: int = 100,
        offset: int = 0,
        run_suuid_list: Optional[List[str]] = None,
        job_name: Optional[str] = None,
        job_suuid: Optional[str] = None,
        project_suuid: Optional[str] = None,
        include_metrics: bool = False,
        include_variables: bool = False,
        ordering: str = "-created",
    ) -> RunList:
        """Get a list of runs

        Args:
            limit (int, optional): Limit the number of runs in the result. Defaults to 100.
            offset (int, optional): Offset the number of runs in the result. Defaults to 0.
            run_suuid_list (List[str], optional): List of run SUUIDs to filter on. Defaults to None.
            job_name (str, optional): Name of the job to filter on. Defaults to None.
            job_suuid (str, optional): SUUID of the job to filter on. Defaults to None.
            project_suuid (str, optional): SUUID of the project to filter on. Defaults to None.
            include_metrics (bool, optional): Include the metrics in the Run dataclass. Defaults to False.
            include_variables (bool, optional): Include the variables in the Run dataclass. Defaults to False.
            ordering (str, optional): Ordering of the run list. Defaults to "-created".

        Returns:
            RunList: List of runs in a RunList dataclass
        """

        return RunSDK().list(
            limit=limit,
            offset=offset,
            run_suuid_list=run_suuid_list,
            job_name=job_name,
            job_suuid=job_suuid,
            project_suuid=project_suuid,
            include_metrics=include_metrics,
            include_variables=include_variables,
            ordering=ordering,
        )


class ResultSDK:
    def get(self, run_suuid: str) -> Union[bytes, None]:
        return RunSDK().result(run_suuid)

    def download(self, run_suuid: str, output_path: Union[Path, str]) -> None:
        RunSDK().result(run_suuid, output_path)

    def get_content_type(self, run_suuid: str) -> str:
        return RunSDK().result_content_type(run_suuid)

    def get_filename(self, run_suuid: str) -> str:
        run = RunSDK().get(run_suuid)

        if run.result:
            return run.result.get("name", "")
        else:
            raise GetError(f"No result found for run SUUID '{run_suuid}'")


class ArtifactSDK:
    def get(self, run_suuid: str) -> Union[bytes, None]:
        return RunSDK().artifact(run_suuid)

    def download(self, run_suuid: str, output_path: Union[Path, str]) -> None:
        RunSDK().artifact(run_suuid, output_path)

    def info(self, run_suuid: str) -> ArtifactInfo:
        return RunSDK().artifact_info(run_suuid)
