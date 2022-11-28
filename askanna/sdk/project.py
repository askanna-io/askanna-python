from typing import List, Optional

from askanna.core.dataclasses.package import Package
from askanna.core.dataclasses.project import Project
from askanna.gateways.project import ProjectGateway

__all__ = [
    "ProjectSDK",
]


class ProjectSDK:
    def __init__(self):
        self.project_gateway = ProjectGateway()

    def list(
        self, workspace_suuid: Optional[str] = None, limit: int = 100, offset: int = 0, ordering: str = "-created"
    ) -> List[Project]:
        return self.project_gateway.list(
            workspace_suuid=workspace_suuid,
            limit=limit,
            offset=offset,
            ordering=ordering,
        )

    def get(self, project_suuid: str) -> Project:
        return self.project_gateway.detail(project_suuid=project_suuid)

    def create(self, workspace_suuid: str, name: str, description: str = "", visibility: str = "PRIVATE") -> Project:
        return self.project_gateway.create(
            workspace_suuid=workspace_suuid,
            name=name,
            description=description,
            visibility=visibility,
        )

    def change(
        self,
        project_suuid: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> Project:
        return self.project_gateway.change(
            project_suuid=project_suuid,
            name=name,
            description=description,
            visibility=visibility,
        )

    def delete(self, project_suuid: str) -> bool:
        return self.project_gateway.delete(project_suuid=project_suuid)

    def package_list(
        self,
        project_suuid: str,
        limit: int = 100,
        offset: int = 0,
        ordering: str = "-created",
    ) -> List[Package]:
        return self.project_gateway.package_list(
            project_suuid=project_suuid,
            limit=limit,
            offset=offset,
            ordering=ordering,
        )
