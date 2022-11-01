import datetime
import uuid
from dataclasses import dataclass


@dataclass
class Job:
    name: str
    description: str
    uuid: uuid.UUID
    short_uuid: str
    project: dict
    notifications: dict
    schedules: list
    created: datetime.datetime
    modified: datetime.datetime
    environment: str
    timezone: str
