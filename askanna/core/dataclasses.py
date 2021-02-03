from dataclasses import dataclass
import datetime
import uuid


@dataclass
class Job:
    name: str
    description: str
    default_payload: str
    uuid: uuid.UUID
    short_uuid: str
    project: uuid.UUID
    created: datetime.datetime
    modified: datetime.datetime
    deleted: datetime.datetime
    backend: str
    environment: str
    visible: int
    owner: str
    title: str  # not used anymore
    function: str  # not used anymore
    env_variables: str  # not used anymore


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
        return f'{self.name} {self.short_uuid}'


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
        return f'{self.title} {self.short_uuid}'

    @property
    def name(self):
        return self.title
