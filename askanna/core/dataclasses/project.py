import datetime
import uuid
from dataclasses import dataclass
from typing import Optional


@dataclass
class Project:
    name: str
    description: str
    uuid: uuid.UUID
    short_uuid: str
    created_by: dict
    package: dict
    notifications: dict
    permission: dict
    visibility: str
    created: datetime.datetime
    modified: datetime.datetime
    workspace: dict
    is_member: bool
    url: Optional[str] = None

    def __str__(self):
        return f"{self.name} {self.short_uuid}"


@dataclass
class Variable:
    name: str
    value: str
    short_uuid: str
    uuid: uuid.UUID
    is_masked: bool
    created: datetime.datetime
    modified: datetime.datetime
    project: dict
