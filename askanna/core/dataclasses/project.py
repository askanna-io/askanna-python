import datetime
from dataclasses import dataclass
from typing import Dict, Optional

from dateutil import parser as dateutil_parser

from askanna.core.dataclasses.workspace import WorkspaceRelation


@dataclass
class Project:
    suuid: str
    name: str
    description: str
    created_by: dict
    package: dict
    permission: dict
    visibility: str
    created: datetime.datetime
    modified: datetime.datetime
    workspace: WorkspaceRelation
    is_member: bool
    url: Optional[str] = None

    def __str__(self):
        return f"{self.name} {self.suuid}"

    @classmethod
    def from_dict(cls, data: Dict) -> "Project":
        data["created"] = dateutil_parser.parse(data["created"])
        data["modified"] = dateutil_parser.parse(data["modified"])

        workspace = WorkspaceRelation.from_dict(data["workspace"])
        del data["workspace"]

        return cls(workspace=workspace, **data)


@dataclass
class ProjectRelation:
    suuid: str
    name: str

    @classmethod
    def from_dict(cls, data: Dict) -> "ProjectRelation":
        del data["relation"]
        return cls(**data)


@dataclass
class Variable:
    suuid: str
    name: str
    value: str
    is_masked: bool
    project: ProjectRelation
    workspace: WorkspaceRelation
    created: datetime.datetime
    modified: datetime.datetime

    @classmethod
    def from_dict(cls, data: Dict) -> "Variable":
        data["created"] = dateutil_parser.parse(data["created"])
        data["modified"] = dateutil_parser.parse(data["modified"])

        project = ProjectRelation.from_dict(data["project"])
        del data["project"]
        workspace = WorkspaceRelation.from_dict(data["workspace"])
        del data["workspace"]

        return cls(project=project, workspace=workspace, **data)
