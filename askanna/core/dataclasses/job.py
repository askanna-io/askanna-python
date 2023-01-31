import datetime
from dataclasses import dataclass
from typing import Dict

from dateutil import parser as dateutil_parser

from .relation import ProjectRelation, WorkspaceRelation


@dataclass
class Job:
    suuid: str
    name: str
    description: str
    environment: str
    timezone: str
    schedules: list
    notifications: dict
    project: ProjectRelation
    workspace: WorkspaceRelation
    created: datetime.datetime
    modified: datetime.datetime

    @classmethod
    def from_dict(cls, data: Dict) -> "Job":
        data["created"] = dateutil_parser.parse(data["created"])
        data["modified"] = dateutil_parser.parse(data["modified"])

        project = ProjectRelation.from_dict(data["project"])
        del data["project"]
        workspace = WorkspaceRelation.from_dict(data["workspace"])
        del data["workspace"]

        return cls(project=project, workspace=workspace, **data)


@dataclass
class Payload:
    suuid: str
    size: int
    lines: int
    created: datetime.datetime
    modified: datetime.datetime

    def __str__(self):
        return (
            f"Payload: {self.suuid} ({self.size} byte"
            + ("s" if self.size != 1 else "")
            + f" & {self.lines} line"
            + ("s" if self.lines != 1 else "")
            + ")"
        )

    def __repr__(self):
        return f"Payload(suuid='{self.suuid}', size={self.size}, lines={self.lines})"

    @classmethod
    def from_dict(cls, data: Dict) -> "Payload":
        data["created"] = dateutil_parser.parse(data["created"])
        data["modified"] = dateutil_parser.parse(data["modified"])
        return cls(**data)
