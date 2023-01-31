from typing import List, Optional

from askanna.config import config
from askanna.core.dataclasses.job import Job
from askanna.core.dataclasses.run import RunStatus
from askanna.core.exceptions import GetError
from askanna.gateways.job import JobGateway

from .mixins import ListMixin

__all__ = [
    "JobSDK",
]


class JobSDK(ListMixin):
    """Management of jobs in AskAnna
    This class is a wrapper around the JobGateway and can be used to manage jobs in Python.
    """

    gateway = JobGateway()
    job_suuid = None

    def _get_job_suuid(self) -> str:
        if not self.job_suuid:
            raise ValueError("No job SUUID set")

        return self.job_suuid

    def list(
        self,
        project_suuid: Optional[str] = None,
        workspace_suuid: Optional[str] = None,
        number_of_results: int = 100,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Job]:
        """List all jobs with filter and order options

        Args:
            project_suuid (str, optional): Project SUUID to filter for jobs in a project. Defaults to None.
            workspace_suuid (str, optional): Workspace SUUID to filter for jobs in a workspace. Defaults to None.
            number_of_results (int): Number of jobs to return. Defaults to 100.
            order_by (str, optional): Order by field(s).
            search (str, optional): Search for a specific job.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            List[Job]: A list of jobs. List items are of type Job dataclass.
        """
        return super().list(
            number_of_results=number_of_results,
            order_by=order_by,
            other_query_params={
                "project_suuid": project_suuid,
                "workspace_suuid": workspace_suuid,
                "search": search,
            },
        )

    def get(self, job_suuid: str) -> Job:
        """Get information of a job

        Args:
            job_suuid (str): SUUID of the job

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Job: Job information in a Job dataclass
        """
        return self.gateway.detail(job_suuid)

    def get_job_by_name(
        self,
        job_name: str,
        project_suuid: Optional[str] = None,
    ) -> Job:
        """Get information of a job by searching on the job name. This only works if the job name is unique, or unique
        within a project.

        Args:
            job_name (str): Name of the job you are looking for
            project_suuid (str, optional): Project SUUID to filter for jobs in a project. Defaults to None.

        Raises:
            GetError: If the job name is not unique or not found

        Returns:
            Job: Job information in a Job dataclass
        """
        job_list = self.list(project_suuid=project_suuid, search=job_name)

        # The above list contain all jobs where the name of the job contains the job name we are looking for.
        # We need to filter on the exact name.
        matching_jobs = list(filter(lambda x: x.name == job_name, job_list))
        if len(matching_jobs) == 0:
            raise GetError("A job with this name is not available. Did you push your code?")
        if len(matching_jobs) > 1:
            if not project_suuid:
                raise GetError(
                    "There are multiple jobs with the same name. You can narrow the selection by providing the "
                    "project SUUID."
                )
            raise GetError(
                "There are multiple jobs with the same name. This could happen if you changed names of the job "
                "manually. Please make sure the job names are unique."
            )

        return matching_jobs[0]

    def run_request(
        self,
        job_suuid: Optional[str] = None,
        data: Optional[dict] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        project_suuid: Optional[str] = None,
        job_name: Optional[str] = None,
    ) -> RunStatus:
        """Do a request to run a job on the AskAnna platform

        Args:
            job_suuid (str, optioanl): SUUID of the job you want to start a run of. job_suuid or job_name is required.
            data (dict, optional): Data to pass to the job.
            name (str, optional): Optionally give the run a name
            description (str, optional): Optionally give the run a description
            project_suuid (str, optional): Project SUUID to filter for jobs in a project. Defaults to None.
            job_name (str, optional): Name of the job you want to start a run of. job_name or job_suuid is required.

        Raises:
            PostError: Error based on response status code with the error message from the API

        Returns:
            RunStatus: The run status information in a RunStatus dataclass
        """
        assert job_suuid or job_name, "To start a run we need at least a job SUUID or job name"
        assert not (job_suuid and job_name), "Parameters 'job_suuid' and 'job_name' are both set. Please only set one."

        if job_name:
            project_suuid = project_suuid or config.project.project_suuid
            job_suuid = self.get_job_by_name(job_name=job_name, project_suuid=project_suuid).suuid
        if not job_suuid:
            raise ValueError("No job SUUID set")

        return self.gateway.run_request(
            job_suuid=job_suuid,
            data=data,
            name=name,
            description=description,
        )

    def change(
        self,
        job_suuid: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Job:
        """Change the name and/or description of a job

        Args:
            job_suuid (str): SUUID of the job you want to change the information of
            name (str, optional): New name for the project. Defaults to None.
            description (str, optional): New description of the project. Defaults to None.

        Raises:
            ValueError: Error when visibility is not "PUBLIC" or "PRIVATE"
            ValueError: Error if none of the arguments 'name', 'description' or 'visibility' are provided
            PatchError: Error based on response status code with the error message from the API

        Returns:
            Project: The changed project information in a Project dataclass
        """
        return self.gateway.change(
            job_suuid=job_suuid,
            name=name,
            description=description,
        )

    def delete(self, job_suuid: str) -> bool:
        """Delete a job

        Args:
            job_suuid (str): SUUID of the job you want to delete

        Raises:
            DeleteError: Error based on response status code with the error message from the API

        Returns:
            bool: True if the job was succesfully deleted
        """
        return self.gateway.delete(job_suuid=job_suuid)
