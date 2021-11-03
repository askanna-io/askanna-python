"""
Core functions for management of runs in AskAnna
This is the class which act as gateway to the API of AskAnna
"""
from typing import List

from askanna.core import exceptions
from askanna.core.apiclient import client
from askanna.core.dataclasses import Run, RunInfo, RunStatus
from askanna.core.job import JobGateway
from askanna.core.metrics import MetricGateway
from askanna.core.variables_tracked import VariableTrackedGateway


class RunGateway:
    def __init__(self, *args, **kwargs):
        self.client = client
        self.run_suuid = None

        # instantiated gateways for query job, metrics and variables
        self.job = JobGateway()
        self.metrics = MetricGateway()
        self.variables = VariableTrackedGateway()

    def start(
        self,
        job_suuid: str = None,
        data: dict = None,
        name: str = None,
        description: str = None,
    ) -> Run:

        url = f"{self.client.base_url}run/{job_suuid}/"

        r = self.client.post(
            url,
            json=data,
            params={
                "name": name,
                "description": description,
            },
        )
        if r.status_code != 200:
            raise exceptions.PostError(
                "{} - Something went wrong while starting a "
                "run: {}".format(r.status_code, r.reason)
            )
        run = Run(**r.json())
        self.run_suuid = run.short_uuid

        return run

    def list(self, query_params: dict = None) -> List[RunInfo]:
        url = f"{self.client.base_url}runinfo/"
        r = self.client.get(url, params=query_params)
        if r.status_code != 200:
            raise exceptions.GetError(
                "{} - Something went wrong while retrieving the status "
                "of the run: {}".format(r.status_code, r.reason)
            )
        return [RunInfo(**r) for r in r.json().get("results")]

    def detail(self, suuid: str = None) -> RunInfo:
        """
        Retrieve details on a Run
        The suuid is optional and can be retrieved from `self.run_suuid`
        if the gateway was instantiated with it.

        returns RunInfo
        """
        suuid = suuid or self.run_suuid
        url = f"{self.client.base_url}runinfo/{suuid}/"

        r = self.client.get(url)
        if r.status_code != 200:
            raise exceptions.GetError(
                "{} - Something went wrong while retrieving the status "
                "of the run: {}".format(r.status_code, r.reason)
            )

        return RunInfo(**r.json())

    def status(self, suuid: str = None) -> RunStatus:
        suuid = suuid or self.run_suuid

        if not suuid:
            raise exceptions.RunError(
                "There is no run SUUID provided. Did you start a run?"
            )

        url = f"{self.client.base_url}status/{suuid}/"

        r = self.client.get(url)
        if r.status_code != 200:
            raise exceptions.GetError(
                "{} - Something went wrong while retrieving the status "
                "of the run: {}".format(r.status_code, r.reason)
            )

        return RunStatus(**r.json())


class RunActionGateway:
    """
    This provides to query runs, using the RunGateway
    the .get() returns eiter
    """

    multiple = False
    run_suuid = None

    def __init__(self):
        self.gateway = RunGateway()

    def start(
        self,
        job_suuid: str = None,
        data: dict = None,
        job_name: str = None,
        project_suuid: str = None,
        name: str = None,
        description: str = None,
    ) -> Run:
        if not job_suuid and not job_name:
            raise exceptions.PostError(
                "To start a run we need at least a job SUUID or job name"
            )
        elif not job_suuid:
            if not project_suuid:
                project_suuid = self.gateway.client.config.project.project_suuid
            job_suuid = self.gateway.job.get_job_by_name(job_name=job_name, project_suuid=project_suuid).short_uuid

        run = self.gateway.start(
            job_suuid=job_suuid,
            data=data,
            name=name,
            description=description,
        )
        self.run_suuid = run.short_uuid
        return run

    def status(self, suuid: str = None) -> RunStatus:
        suuid = suuid or self.run_suuid
        return self.gateway.status(suuid=suuid)

    def get(
        self,
        run,
        include_metrics: bool = False,
        include_variables: bool = False,
    ) -> RunInfo:
        if not run:
            raise exceptions.GetError(
                "Please specify the run SUUID to 'get' a run"
            )

        runinfo = self.gateway.detail(suuid=run)
        if include_metrics:
            # also fetch the metrics for the runs
            metrics = self.gateway.metrics.get(run=runinfo.short_uuid)
            # run.metrics
            runinfo.metrics = metrics

        if include_variables:
            # also fetch the variables for the runs
            variables = self.gateway.variables.get(run=runinfo.short_uuid)
            # add the metrics to the runobjects
            # run.variables
            runinfo.variables = variables

        return runinfo


class RunMultipleQueryGateway(RunActionGateway):
    def get_query(self, project: str = None, job: str = None, runs: list = None):
        """
        We return jobs/ metrics from either:
        - project
        - job
        - runs (specific run_suuids)

        When runs is set, this takes precedence over project and job.
        When runs is empty, look at project or job, where job takes precedence
        """
        query = {}
        if runs and len(runs):
            # build comma separated string from runs if more then 1 run
            query = {"runs": ",".join(runs)}
        if project:
            query.update({"project": project})
        if job:
            query.update({"job": job})
        return query

    def get(
        self,
        project: str = None,
        job: str = None,
        job_name: str = None,
        runs: list = None,
        limit: int = 100,
        offset: int = 0,
        ordering: str = "-created",
        include_metrics: bool = False,
        include_variables: bool = False,
    ) -> List[RunInfo]:
        if job and job_name:
            raise exceptions.GetError(
                "Parameters 'job' and 'job_name' are both set. Please use 'job' or 'job_name'."
            )
        if job_name:
            project_suuid = project or self.gateway.client.config.project.project_suuid
            job = self.gateway.job.get_job_by_name(job_name=job_name, project_suuid=project_suuid).short_uuid

        query = self.get_query(project, job, runs)
        query.update(
            {
                "limit": limit,
                "offset": offset,
                "ordering": ordering,
            }
        )
        rgw = RunGateway()
        runs = rgw.list(query_params=query)
        if include_metrics:
            # also fetch the metrics for the runs
            for run in runs:
                metrics = self.gateway.metrics.get(run=run.short_uuid)
                # run.metrics
                run.metrics = metrics

        if include_variables:
            # also fetch the variables for the runs
            for run in runs:
                variables = self.gateway.variables.get(run=run.short_uuid)
                # run.metrics
                run.variables = variables

        return runs
