import datetime
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Union


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


@dataclass
class Package:
    filename: str
    name: Union[str, None]
    description: str
    uuid: uuid.UUID
    short_uuid: str
    project: dict
    size: int
    original_filename: str
    created_by: dict
    member: uuid.UUID
    created: datetime.datetime
    modified: datetime.datetime
    deleted: Union[datetime.datetime, None] = None
    finished: Union[datetime.datetime, None] = None


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
    url: Union[str, None] = None

    def __str__(self):
        return f"{self.name} {self.short_uuid}"


@dataclass
class Run:
    """
    This dataclass holds information about the run which just started
    """

    message_type: str
    status: str
    uuid: uuid.UUID
    short_uuid: str
    name: str
    next_url: str
    job: dict
    workspace: dict
    project: dict
    created: datetime.datetime
    updated: datetime.datetime
    finished: Union[datetime.datetime, None] = None
    duration: int = 0


@dataclass
class RunStatus:
    """
    This dataclass holds information about the status of a run.
    """

    message_type: str
    status: str
    uuid: uuid.UUID
    short_uuid: str
    name: str
    next_url: str
    job: dict
    workspace: dict
    project: dict
    environment: dict
    created: datetime.datetime
    updated: datetime.datetime
    finished: Union[datetime.datetime, None] = None
    duration: int = 0


@dataclass
class RunInfo:
    uuid: uuid.UUID
    short_uuid: str
    name: str
    description: str

    status: str
    duration: int

    trigger: dict
    created_by: dict

    package: dict
    payload: dict
    result: dict
    artifact: dict
    metrics_meta: dict
    variables_meta: dict
    log: dict
    environment: dict

    job: dict
    project: dict
    workspace: dict

    created: datetime.datetime
    modified: datetime.datetime
    started: Union[datetime.datetime, None] = None
    finished: Union[datetime.datetime, None] = None

    metrics = []
    variables = []


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
    run_suuid: Union[str, None] = None
    created: Union[datetime.datetime, None] = None

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


@dataclass
class VariableDataPair:
    name: str
    value: Any
    dtype: str

    def to_dict(self, yes=True) -> Dict:
        return {"name": self.name, "value": self.value, "type": self.dtype}


@dataclass
class VariableLabel:
    name: str
    value: Any
    dtype: str

    def to_dict(self, yes=True) -> Dict:
        return {"name": self.name, "value": self.value, "type": self.dtype}


@dataclass
class VariableTracked:
    variable: VariableDataPair
    label: List[VariableLabel] = field(default_factory=list)
    run_suuid: Union[str, None] = None
    created: Union[datetime.datetime, None] = None

    def __post_init__(self):
        if not self.created:
            # record the created time always in UTC time so that we don't have
            # to figure out what local timezone is, this is always correct
            # and we don't have to calculate back to utc
            self.created = datetime.datetime.now(datetime.timezone.utc)

    def to_dict(self, yes=True) -> Dict:
        return {
            "variable": self.variable.to_dict(),
            "label": [label.to_dict() for label in self.label],
            "run_suuid": self.run_suuid,
            "created": self.created,
        }
