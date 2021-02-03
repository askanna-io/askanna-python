"""
Core functions for management of runs in AskAnna
This is the class which act as gateway to the API of AskAnna
"""
from askanna import job
from askanna.core import client, exceptions
from askanna.core.dataclasses import Run


class RunGateway:
    def __init__(self, *args, **kwargs):
        self.client = client
        self.run_suuid = None

    def start(self, job_suuid: str = None, data: dict = None, job_name: str = None, project_suuid: str = None) -> Run:
        if not job_suuid and not job_name:
            raise exceptions.PostError("To start a run we need at least a job SUUID or job name")
        elif not job_suuid:
            job_suuid = job.get_job_by_name(job_name=job_name, project_suuid=project_suuid).short_uuid

        url = "{}{}/{}/".format(
            self.client.config.remote,
            "run",
            job_suuid
        )

        r = self.client.post(url, json=data)
        if r.status_code != 200:
            raise exceptions.PostError("{} - Something went wrong while starting a "
                                       "run: {}".format(r.status_code, r.reason))
        run = Run(**r.json())
        self.run_suuid = run.short_uuid

        return run

    def status(self, suuid: str = None) -> Run:
        run_suuid = suuid or self.run_suuid

        if not run_suuid:
            raise exceptions.RunError("There is no run UUID provided. Did you start a run?")

        url = "{}{}/{}/".format(
            self.client.config.remote,
            "status",
            run_suuid
        )

        r = self.client.get(url)
        if r.status_code != 200:
            raise exceptions.GetError("{} - Something went wrong while retrieving the status "
                                      "of the run: {}".format(r.status_code, r.reason))

        return Run(**r.json())
