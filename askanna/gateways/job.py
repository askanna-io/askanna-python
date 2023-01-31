from typing import List, Optional

from askanna.core.dataclasses.job import Job
from askanna.core.dataclasses.run import RunStatus
from askanna.core.exceptions import DeleteError, GetError, PatchError, PostError
from askanna.gateways.api_client import client

from .utils import ListResponse


class JobListResponse(ListResponse):
    def __init__(self, data: dict):
        super().__init__(data)
        self.results: List[Job] = [Job.from_dict(job) for job in data["results"]]

    @property
    def jobs(self):
        return self.results


class JobGateway:
    """Management of jobs in AskAnna
    This is the class which act as gateway to the API of AskAnna
    """

    def list(
        self,
        project_suuid: Optional[str] = None,
        workspace_suuid: Optional[str] = None,
        page_size: Optional[int] = None,
        cursor: Optional[str] = None,
        order_by: Optional[str] = None,
        search: Optional[str] = None,
    ) -> JobListResponse:
        """List all jobs with filter and order options

        Args:
            project_suuid (str, optional): Project SUUID to filter for jobs in a project. Defaults to None.
            workspace_suuid (str, optional): Workspace SUUID to filter for jobs in a workspace. Defaults to None.
            page_size (int, optional): Number of jobs to return per page. Defaults to the default value of
                the backend.
            cursor (str, optional): Cursor to start the page from. Defaults to None.
            order_by (str, optional): Order by field(s). Defaults to the default value of the backend.
            search (str, optional): Search for a specific job.

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            JobListResponse: The response from the API with a list of jobs and pagination information
        """
        assert page_size is None or page_size > 0, "page_size must be a positive integer"

        response = client.get(
            url=client.askanna_url.job.job_list(),
            params={
                "project_suuid": project_suuid,
                "workspace_suuid": workspace_suuid,
                "page_size": page_size,
                "cursor": cursor,
                "order_by": order_by,
                "search": search,
            },
        )

        if response.status_code != 200:
            error_message = f"{response.status_code} - Something went wrong while retrieving the job list"
            try:
                error_message += f":\n  {response.json()}"
            except ValueError:
                pass
            raise GetError(error_message)

        return JobListResponse(response.json())

    def detail(self, job_suuid: str) -> Job:
        """Get information of a job

        Args:
            job_suuid (str): SUUID of the job

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Job: Job information in a Job dataclass
        """

        response = client.get(
            url=client.askanna_url.job.job_detail(job_suuid),
        )

        if response.status_code == 404:
            raise GetError(f"404 - The job SUUID '{job_suuid}' was not found")
        if response.status_code != 200:
            raise GetError(
                f"{response.status_code} - Something went wrong while retrieving job SUUID '{job_suuid}': "
                f"{response.json()}"
            )

        return Job.from_dict(response.json())

    def run_request(
        self,
        job_suuid: str,
        data: Optional[dict] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> RunStatus:
        """Do a request to run a job on the AskAnna platform

        Args:
            job_suuid (str): SUUID of the job you want to start a run of

        Raises:
            PostError: Error based on response status code with the error message from the API

        Returns:
            RunStatus: The run status information in a RunStatus dataclass
        """
        response = client.post(
            url=client.askanna_url.job.run_request(job_suuid),
            json=data,
            params={
                "name": name,
                "description": description,
            },
        )

        if response.status_code == 404:
            raise PostError(f"404 - The job SUUID '{job_suuid}' was not found")
        if response.status_code != 201:
            raise PostError(
                f"{response.status_code} - Something went wrong while starting the run for job SUUID '{job_suuid}': "
                f"{response.json()}"
            )

        return RunStatus.from_dict(response.json())

    def change(
        self,
        job_suuid: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Job:
        """Change the name and/or description of a job

        Args:
            job_suuid (str): SUUID of the job you want to change the information of
            name (str, optional): New name for the job. Defaults to None.
            description (str, optional): New description of the job. Defaults to None.

        Raises:
            ValueError: Error if none of the arguments 'name' or 'description' are provided
            PatchError: Error based on response status code with the error message from the API

        Returns:
            Job: The changed job information in a Job dataclass
        """
        changes = {}
        if name:
            changes.update({"name": name})
        if description:
            changes.update({"description": description})

        if not changes:
            raise ValueError("At least one of the parameters 'name' or 'description' must be set")

        response = client.patch(url=client.askanna_url.job.job_detail(job_suuid), json=changes)

        if response.status_code == 404:
            raise PatchError(f"404 - The job SUUID '{job_suuid}' was not found")
        if response.status_code != 200:
            raise PatchError(
                f"{response.status_code} - Something went wrong while updating the job SUUID '{job_suuid}': "
                f"{response.json()}"
            )

        return Job.from_dict(response.json())

    def delete(self, job_suuid: str) -> bool:
        """Delete a job

        Args:
            job_suuid (str): SUUID of the job you want to delete

        Raises:
            DeleteError: Error based on response status code with the error message from the API

        Returns:
            bool: True if the job was succesfully deleted
        """
        response = client.delete(
            url=client.askanna_url.job.job_detail(job_suuid),
        )

        if response.status_code == 404:
            raise DeleteError(f"404 - The job SUUID '{job_suuid}' was not found")
        if response.status_code != 204:
            raise DeleteError(
                f"{response.status_code} - Something went wrong while deleting the job SUUID '{job_suuid}': "
                f"{response.json()}"
            )

        return True
