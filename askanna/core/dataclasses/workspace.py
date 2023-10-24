import datetime
from dataclasses import dataclass
from typing import Dict, Optional

from dateutil import parser as dateutil_parser

from .base import VISIBILITY
from .relation import CreatedByWithAvatarRelation


@dataclass
class Workspace:
    suuid: str
    name: str
    description: str
    visibility: VISIBILITY
    created_by: Optional[CreatedByWithAvatarRelation]
    permission: dict
    is_member: bool
    created_at: datetime.datetime
    modified_at: datetime.datetime

    def __str__(self):
        return f"Workspace: {self.name} ({self.suuid})"

    @classmethod
    def from_dict(cls, data: Dict) -> "Workspace":
        data["created_at"] = dateutil_parser.parse(data["created_at"])
        data["modified_at"] = dateutil_parser.parse(data["modified_at"])

        created_by = CreatedByWithAvatarRelation.from_dict(data["created_by"]) if data["created_by"] else None
        del data["created_by"]

        return cls(created_by=created_by, **data)
