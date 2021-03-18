from dataclasses import dataclass, field
import datetime
from typing import Any, List, Dict
import uuid


@dataclass
class Job:
    name: str
    description: str
    uuid: uuid.UUID
    short_uuid: str
    project: uuid.UUID
    created: datetime.datetime
    modified: datetime.datetime
    environment: str


@dataclass
class Project:
    name: str
    description: str
    uuid: uuid.UUID
    short_uuid: str
    created_by: dict
    package: dict
    status: int
    template: str
    created: datetime.datetime
    modified: datetime.datetime
    workspace: dict

    def __str__(self):
        return f"{self.name} {self.short_uuid}"


@dataclass
class Run:
    message_type: str
    status: str
    uuid: uuid.UUID
    short_uuid: str
    next_url: str
    job: dict
    workspace: dict
    project: dict
    created: datetime.datetime
    updated: datetime.datetime
    finished: datetime.datetime = None


@dataclass
class RunInfo:
    title: str
    description: str
    status: str
    uuid: uuid.UUID
    short_uuid: str
    project: dict
    artifact: dict
    package: dict
    version: dict
    owner: dict
    trigger: dict
    runner: dict
    payload: dict
    jobdef: dict
    metricsmeta: dict
    created: datetime.datetime
    modified: datetime.datetime
    deleted: datetime.datetime
    finished: datetime.datetime = None

    metrics = []


@dataclass
class User:
    short_uuid: str
    name: str
    email: str
    is_active: bool
    date_joined: datetime.datetime
    last_login: datetime.datetime


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


@dataclass
class Workspace:
    title: str
    description: str
    uuid: uuid.UUID
    short_uuid: str
    status: int
    activate_date: datetime.datetime
    deactivate_date: datetime.datetime
    created: datetime.datetime
    modified: datetime.datetime
    deleted: datetime = None

    def __str__(self):
        return f"{self.title} {self.short_uuid}"

    @property
    def name(self):
        return self.title


@dataclass
class MetricDataPair:
    name: str
    value: Any
    dtype: str

    def to_dict(self, yes=True) -> Dict:
        return {"name": self.name, "value": self.value, "type": self.dtype}


@dataclass
class MetricLabel:
    name: str
    value: Any
    dtype: str

    def to_dict(self, yes=True) -> Dict:
        return {"name": self.name, "value": self.value, "type": self.dtype}


@dataclass
class Metric:
    metric: MetricDataPair
    label: List[MetricLabel] = field(default_factory=list)
    run_suuid: str = None
    created: datetime.datetime = None

    def __post_init__(self):
        if not self.created:
            # record the created time always in UTC time so that we don't have
            # to figure out what local timezone is, this is always correct
            # and we don't have to calculate back to utc
            self.created = datetime.datetime.now(datetime.timezone.utc)

    def to_dict(self, yes=True) -> Dict:
        return {
            "metric": self.metric.to_dict(),
            "label": [label.to_dict() for label in self.label],
            "run_suuid": self.run_suuid,
            "created": self.created,
        }
