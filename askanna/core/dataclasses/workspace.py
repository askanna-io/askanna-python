import datetime
from dataclasses import dataclass
from typing import Dict, Optional

from dateutil import parser as dateutil_parser

from .base import VISIBILITY
from .relation import UserRelation


@dataclass
class Workspace:
    suuid: str
    name: str
    description: str
    visibility: VISIBILITY
    created_by: Optional[UserRelation]
    permission: dict
    is_member: bool
    created: datetime.datetime
    modified: datetime.datetime

    def __str__(self):
        return f"{self.name} {self.suuid}"

    @classmethod
    def from_dict(cls, data: Dict) -> "Workspace":
        data["created"] = dateutil_parser.parse(data["created"])
        data["modified"] = dateutil_parser.parse(data["modified"])

        created_by = UserRelation.from_dict(data["created_by"]) if data["created_by"] else None
        del data["created_by"]

        return cls(created_by=created_by, **data)
