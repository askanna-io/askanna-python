import datetime
import uuid
from dataclasses import dataclass
from typing import Optional


@dataclass
class Package:
    filename: str
    name: Optional[str]
    description: str
    uuid: uuid.UUID
    short_uuid: str
    project: dict
    size: int
    original_filename: str
    created_by: dict
    member: uuid.UUID  # type: ignore
    created: datetime.datetime
    modified: datetime.datetime
    deleted: Optional[datetime.datetime] = None
    finished: Optional[datetime.datetime] = None
