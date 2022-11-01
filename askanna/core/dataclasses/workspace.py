import datetime
import uuid
from dataclasses import dataclass


@dataclass
class Workspace:
    uuid: uuid.UUID
    short_uuid: str
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
        return f"{self.name} {self.short_uuid}"
