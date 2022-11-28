from typing import List, Optional

from askanna.core.dataclasses.job import Job
from askanna.core.dataclasses.run import RunStatus
from askanna.core.exceptions import DeleteError, GetError, PatchError, PostError
from askanna.gateways.api_client import client


class JobGateway:
    """Management of jobs in AskAnna
    This is the class which act as gateway to the API of AskAnna
    """

    def list(
        self,
        project_suuid: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        ordering: str = "-created",
    ) -> List[Job]:
        """List all jobs with the option to filter on project

        Args:
            limit (int): Number of results to return. Defaults to 100.
            offset (int): The initial index from which to return the results. Defaults to 0.
            project_suuid (str, optional): Project SUUID to filter for jobs in a project. Defaults to None.
            ordering (str): Ordering of the results. Defaults to "-created".

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            List[Job]: A list of jobs. List items are of type Job dataclass.
        """
        query = {
            "offset": offset,
            "limit": limit,
            "ordering": ordering,
        }

        if project_suuid:
            url = client.askanna_url.project.job_list(project_suuid)
        else:
            url = client.askanna_url.job.job_list()

        r = client.get(url, params=query)
        if r.status_code != 200:
            raise GetError(f"{r.status_code} - Something went wrong while retrieving jobs: {r.json()}")

        return [Job.from_dict(job) for job in r.json().get("results")]

    def detail(self, job_suuid: str) -> Job:
        """Get information of a job

        Args:
            job_suuid (str): SUUID of the job

        Raises:
            GetError: Error based on response status code with the error message from the API

        Returns:
            Job: Job information in a Job dataclass
        """
        url = client.askanna_url.job.job_detail(job_suuid)
        r = client.get(url)

        if r.status_code == 200:
            return Job.from_dict(r.json())
        if r.status_code == 404:
            raise GetError(f"404 - The job SUUID '{job_suuid}' was not found")
        raise GetError(f"{r.status_code} - Something went wrong while retrieving job SUUID '{job_suuid}': {r.json()}")

    # TODO: move to job core and don't do this in Gateway
    def get_job_by_name(self, job_name: str, project_suuid: Optional[str] = None) -> Job:
        """Get information of a job by searching on the job name. This only works if the job name is unique. Or unique
        within a project.

        Args:
            job_name (str): Name of the job you are looking for
            project_suuid (str, optional): Project SUUID to filter for jobs in a project. Defaults to None.

        Raises:
            GetError: If the job name is not unique or not found

        Returns:
            Job: Job information in a Job dataclass
        """
        job_list = self.list(project_suuid=project_suuid)

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
        url = client.askanna_url.job.run_request(job_suuid)
        r = client.post(
            url,
            json=data,
            params={
                "name": name,
                "description": description,
            },
        )

        if r.status_code == 200:
            return RunStatus.from_dict(r.json())
        if r.status_code == 404:
            raise PostError(f"404 - The job SUUID '{job_suuid}' was not found")
        raise PostError(
            f"{r.status_code} - Something went wrong while starting the run for job SUUID '{job_suuid}': {r.json()}"
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

        url = client.askanna_url.job.job_detail(job_suuid)
        r = client.patch(url, json=changes)

        if r.status_code == 200:
            return Job.from_dict(r.json())
        if r.status_code == 404:
            raise PatchError(f"404 - The job SUUID '{job_suuid}' was not found")
        raise PatchError(
            f"{r.status_code} - Something went wrong while updating the job SUUID '{job_suuid}': {r.json()}"
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
        url = client.askanna_url.job.job_detail(job_suuid)
        r = client.delete(url)

        if r.status_code == 204:
            return True
        if r.status_code == 404:
            raise DeleteError(f"404 - The job SUUID '{job_suuid}' was not found")
        raise DeleteError(
            f"{r.status_code} - Something went wrong while deleting the job SUUID '{job_suuid}': {r.json()}"
        )
