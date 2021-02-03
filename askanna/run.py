"""
Management of runs in AskAnna
"""
from askanna.core.dataclasses import Run
from askanna.core.run import RunGateway


def start(job_suuid: str = None, data: dict = None, job_name: str = None, project_suuid: str = None) -> Run:
    g = RunGateway()
    run = g.start(job_suuid=job_suuid, data=data, job_name=job_name, project_suuid=project_suuid)

    return run


def status(suuid: str) -> Run:
    g = RunGateway()
    status = g.status(suuid=suuid)

    return status
