import datetime
from dataclasses import dataclass
from typing import Dict, Optional

from dateutil import parser as dateutil_parser

from .base import VISIBILITY
from .relation import PackageRelation, UserRelation, WorkspaceRelation


@dataclass
class Project:
    suuid: str
    name: str
    description: str
    visibility: VISIBILITY
    workspace: WorkspaceRelation
    package: Optional[PackageRelation]
    created_by: Optional[UserRelation]
    is_member: bool
    permission: dict
    created_at: datetime.datetime
    modified_at: datetime.datetime

    def __str__(self):
        return f"Project: {self.name} ({self.suuid})"

    @classmethod
    def from_dict(cls, data: Dict) -> "Project":
        data["created_at"] = dateutil_parser.parse(data["created_at"])
        data["modified_at"] = dateutil_parser.parse(data["modified_at"])

        workspace = WorkspaceRelation.from_dict(data["workspace"])
        del data["workspace"]

        package = PackageRelation.from_dict(data["package"]) if data["package"] else None
        del data["package"]

        created_by = UserRelation.from_dict(data["created_by"]) if data["created_by"] else None
        del data["created_by"]

        return cls(workspace=workspace, package=package, created_by=created_by, **data)
