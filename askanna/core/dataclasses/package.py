import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional

from dateutil import parser as dateutil_parser

from .relation import ProjectRelation, WorkspaceRelation


@dataclass
class Package:
    suuid: str
    workspace: WorkspaceRelation
    project: ProjectRelation
    created_by: dict
    created: datetime.datetime
    modified: datetime.datetime
    name: Optional[str]
    description: str
    filename: str
    size: int
    cdn_base_url: Optional[str] = None
    files: Optional[List] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "Package":
        data["created"] = dateutil_parser.parse(data["created"])
        data["modified"] = dateutil_parser.parse(data["modified"])

        workspace = WorkspaceRelation.from_dict(data["workspace"])
        del data["workspace"]
        project = ProjectRelation.from_dict(data["project"])
        del data["project"]

        return cls(workspace=workspace, project=project, **data)
