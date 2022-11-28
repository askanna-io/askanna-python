from typing import List, Optional

from askanna.core.dataclasses.workspace import Workspace
from askanna.gateways.workspace import WorkspaceGateway

__all__ = [
    "WorkspaceSDK",
]


class WorkspaceSDK:
    def __init__(self):
        self.workspace_gateway = WorkspaceGateway()

    def list(self, limit: int = 100, offset: int = 0, ordering: str = "-created") -> List[Workspace]:
        return self.workspace_gateway.list(
            limit=limit,
            offset=offset,
            ordering=ordering,
        )

    def get(self, workspace_suuid: str) -> Workspace:
        return self.workspace_gateway.detail(workspace_suuid=workspace_suuid)

    def create(self, name: str, description: str = "", visibility: str = "PRIVATE") -> Workspace:
        return self.workspace_gateway.create(
            name=name,
            description=description,
            visibility=visibility,
        )

    def change(
        self,
        workspace_suuid: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> Workspace:
        return self.workspace_gateway.change(
            workspace_suuid=workspace_suuid,
            name=name,
            description=description,
            visibility=visibility,
        )

    def delete(self, workspace_suuid: str) -> bool:
        return self.workspace_gateway.delete(workspace_suuid=workspace_suuid)
