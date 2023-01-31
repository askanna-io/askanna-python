from dataclasses import dataclass
from typing import Dict

from .base import MembershipRole


@dataclass
class BaseRelation:
    relation: str
    suuid: str
    name: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]):
        return cls(**data)


@dataclass
class WorkspaceRelation(BaseRelation):
    ...


@dataclass
class ProjectRelation(BaseRelation):
    ...


@dataclass
class PackageRelation(BaseRelation):
    ...


@dataclass
class JobRelation(BaseRelation):
    ...


@dataclass
class UserRelation:
    relation: str
    suuid: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "UserRelation":
        return cls(**data)


@dataclass
class CreatedByRelation(BaseRelation):
    job_title: str
    role: MembershipRole
    status: str

    @classmethod
    def from_dict(cls, data: Dict) -> "CreatedByRelation":
        role = MembershipRole(**data["role"])
        del data["role"]

        return cls(role=role, **data)


@dataclass
class CreatedByWithAvatarRelation(CreatedByRelation):
    avatar: dict


@dataclass
class PayloadRelation(BaseRelation):
    size: int
    lines: int
