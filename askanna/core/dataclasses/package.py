import datetime
from dataclasses import dataclass
from typing import Dict, Optional

from dateutil import parser as dateutil_parser

from askanna.core.dataclasses.project import ProjectRelation
from askanna.core.dataclasses.workspace import WorkspaceRelation


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

    @classmethod
    def from_dict(cls, data: Dict) -> "Package":
        data["created"] = dateutil_parser.parse(data["created"])
        data["modified"] = dateutil_parser.parse(data["modified"])

        workspace = WorkspaceRelation.from_dict(data["workspace"])
        del data["workspace"]
        project = ProjectRelation.from_dict(data["project"])
        del data["project"]

        return cls(workspace=workspace, project=project, **data)


@dataclass
class PackageRelation:
    suuid: str
    name: str

    @classmethod
    def from_dict(cls, data: Dict) -> "PackageRelation":
        del data["relation"]
        return cls(**data)
