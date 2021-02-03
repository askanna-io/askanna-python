"""
Management of jobs in AskAnna
"""
from askanna.core.job import JobGateway
from askanna.core.dataclasses import Job


def list(project_suuid: str = None) -> list:
    g = JobGateway()
    return g.list(project_suuid=project_suuid)


def get_job_by_name(job_name: str, project_suuid: str = None) -> Job:
    g = JobGateway()
    return g.get_job_by_name(job_name=job_name, project_suuid=project_suuid)
