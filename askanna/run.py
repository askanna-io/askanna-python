"""
Management of runs in AskAnna
"""

from askanna.core.run import RunGateway


def start(job_suuid=None, data=None, job_name=None, project=None):
    g = RunGateway()
    run = g.start(job_suuid=job_suuid, data=data, job_name=job_name, project=project)

    return run


def status(run_suuid):
    g = RunGateway()
    status = g.status(run_suuid=run_suuid)

    return status
