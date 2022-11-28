from typing import List, Optional

from askanna.core.dataclasses.job import Job
from askanna.gateways.job import JobGateway

__all__ = [
    "JobSDK",
]


class JobSDK:
    def __init__(self):
        self.job_gateway = JobGateway()

    def list(
        self, project_suuid: Optional[str] = None, limit: int = 100, offset: int = 0, ordering: str = "-created"
    ) -> List[Job]:
        return self.job_gateway.list(project_suuid=project_suuid, limit=limit, offset=offset, ordering=ordering)

    def get(self, job_suuid: str) -> Job:
        return self.job_gateway.detail(job_suuid=job_suuid)

    def get_job_by_name(self, job_name: str, project_suuid: Optional[str] = None) -> Job:
        return self.job_gateway.get_job_by_name(job_name=job_name, project_suuid=project_suuid)

    def change(self, job_suuid: str, name: Optional[str] = None, description: Optional[str] = None) -> Job:
        return self.job_gateway.change(job_suuid=job_suuid, name=name, description=description)

    def delete(self, job_suuid: str) -> bool:
        return self.job_gateway.delete(job_suuid=job_suuid)
