import datetime
from dataclasses import dataclass
from typing import Dict

from dateutil import parser as dateutil_parser


@dataclass
class Workspace:
    suuid: str
    name: str
    description: str
    visibility: str
    created_by: dict
    permission: dict
    is_member: bool
    created: datetime.datetime
    modified: datetime.datetime
    url: str

    def __str__(self):
        return f"{self.name} {self.suuid}"

    @classmethod
    def from_dict(cls, data: Dict) -> "Workspace":
        data["created"] = dateutil_parser.parse(data["created"])
        data["modified"] = dateutil_parser.parse(data["modified"])
        return cls(**data)


@dataclass
class WorkspaceRelation:
    suuid: str
    name: str

    @classmethod
    def from_dict(cls, data: Dict) -> "WorkspaceRelation":
        del data["relation"]
        return cls(**data)
