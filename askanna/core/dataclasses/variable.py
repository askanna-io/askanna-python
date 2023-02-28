import datetime
from dataclasses import dataclass
from typing import Dict

from dateutil import parser as dateutil_parser

from .relation import ProjectRelation, WorkspaceRelation


@dataclass
class Variable:
    suuid: str
    name: str
    value: str
    is_masked: bool
    project: ProjectRelation
    workspace: WorkspaceRelation
    created_at: datetime.datetime
    modified_at: datetime.datetime

    @classmethod
    def from_dict(cls, data: Dict) -> "Variable":
        data["created_at"] = dateutil_parser.parse(data["created_at"])
        data["modified_at"] = dateutil_parser.parse(data["modified_at"])

        project = ProjectRelation.from_dict(data["project"])
        del data["project"]
        workspace = WorkspaceRelation.from_dict(data["workspace"])
        del data["workspace"]

        return cls(project=project, workspace=workspace, **data)
