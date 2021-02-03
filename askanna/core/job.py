"""
Management of jobs in AskAnna
This is the class which act as gateway to the API of AskAnna
"""
from askanna.core import client, exceptions
from askanna.core.dataclasses import Job


class JobGateway:
    def __init__(self, *args, **kwargs):
        self.client = client

    def list(self, project_suuid: str = None) -> list:
        if project_suuid:
            # build url to select for project only
            url = "{}{}/{}/{}".format(
                self.client.config.remote,
                "project",
                project_suuid,
                "jobs"
            )
        else:
            url = "{}{}/".format(
                self.client.config.remote,
                "job"
            )

        r = self.client.get(url)
        if r.status_code != 200:
            raise exceptions.GetError("{} - Something went wrong while retrieving "
                                      "jobs: {}".format(r.status_code, r.json()))

        return [Job(**job) for job in r.json()]

    def get_job_by_name(self, job_name: str, project_suuid: str = None) -> Job:
        job_name = job_name.strip()
        job_list = self.list(project_suuid=project_suuid)
        result = None

        matching_jobs = list(filter(lambda x: x.name == job_name, job_list))
        if len(matching_jobs) == 0:
            raise exceptions.GetError("A job with this name is not available. Did you push your "
                                      "code?")

        if len(matching_jobs) > 1:
            raise exceptions.GetError("There are multiple jobs with the same name. You can "
                                      "narrow the selection by providing the project "
                                      "SUUID.")
        result = matching_jobs[0]
        return result
