"""
Management of jobs in AskAnna
"""

from askanna.core.job import JobGateway
from askanna.core.project import Project


def list(project: Project = None):
    g = JobGateway()
    return g.list(project=project)


def get_job_by_name(job_name, project: Project = None):
    g = JobGateway()
    return g.get_job_by_name(job_name, project)
