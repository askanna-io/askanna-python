import datetime
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from dateutil import parser as dateutil_parser

from askanna.core.exceptions import MultipleObjectsReturnedError
from askanna.core.utils.object import json_serializer

from .base import Label
from .relation import (
    CreatedByRelation,
    CreatedByWithAvatarRelation,
    JobRelation,
    PayloadRelation,
    ProjectRelation,
    RunRelation,
    WorkspaceRelation,
)

try:
    from typing import Literal
except ImportError:  # pragma: no cover
    from typing_extensions import Literal

STATUS = Literal["queued", "running", "finished", "failed"]
TRIGGER = Literal["api", "cli", "python-sdk", "webui", "schedule", "worker"]


@dataclass
class Variable:
    name: str
    value: Any
    type: str

    def __str__(self):
        return f"{self.name}: {self.value}"

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "type": self.type,
        }


@dataclass
class VariableObject:
    variable: Variable
    label: List[Label] = field(default_factory=list)
    run_suuid: Optional[str] = None
    created_at: Optional[datetime.datetime] = None

    def __post_init__(self):
        if not self.created_at:
            # The created time is set with timezome set to UTC so that we don't have to figure out what the local
            # timezone is. UTC is the default timezone for the API.
            self.created_at = datetime.datetime.now(datetime.timezone.utc)

    def __str__(self):
        return f"{self.variable} ({len(self.label)} label" + ("s" if len(self.label) != 1 else "") + ")"

    def __repr__(self):
        return f"VariableObject({self.variable})"

    def to_dict(self) -> Dict:
        return {
            "variable": self.variable.to_dict(),
            "label": [label.to_dict() for label in self.label],
            "run_suuid": self.run_suuid,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "VariableObject":
        return cls(
            variable=Variable(
                name=data["variable"]["name"],
                value=data["variable"]["value"],
                type=data["variable"]["type"],
            ),
            label=[Label(**label) for label in data["label"]],
            run_suuid=data["run_suuid"],
            created_at=dateutil_parser.isoparse(data["created_at"]),
        )


@dataclass
class VariableList:
    variables: List[VariableObject] = field(default_factory=list)

    def __len__(self):
        return len(self.variables)

    def __iter__(self):
        yield from self.variables

    def __getitem__(self, row):
        return self.variables[row]

    def __str__(self):
        return f"List of {len(self.variables)} variable" + ("s" if len(self.variables) != 1 else "")

    def __repr__(self):
        return f"VariableList({len(self.variables)} variable" + ("s" if len(self.variables) != 1 else "") + ")"

    def append(self, variable: VariableObject):
        self.variables.append(variable)

    def get(self, name) -> Union[VariableObject, None]:
        variables_filtered = self.filter(name)
        if len(variables_filtered) == 1:
            return variables_filtered[0]
        if len(variables_filtered) > 1:
            raise MultipleObjectsReturnedError(
                f"Found multiple variables matching name '{name}', please use the method .filter(name=\"{name}\")."
            )
        return None

    def filter(self, name) -> List[VariableObject]:
        variables_filtered = list(filter(lambda x: x.variable.name == name, self.variables))
        return variables_filtered

    def to_dict(self) -> List[dict]:
        return [variable.to_dict() for variable in self.variables]

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=json_serializer)


@dataclass
class Metric(Variable):
    pass


@dataclass
class MetricObject:
    metric: Metric
    label: List[Label] = field(default_factory=list)
    run_suuid: Optional[str] = None
    created_at: Optional[datetime.datetime] = None

    def __post_init__(self):
        if not self.created_at:
            # The created time is set with timezome set to UTC so that we don't have to figure out what the local
            # timezone is. UTC is the default timezone for the API.
            self.created_at = datetime.datetime.now(datetime.timezone.utc)

    def __str__(self):
        return f"{self.metric} ({len(self.label)} label" + ("s" if len(self.label) != 1 else "") + ")"

    def __repr__(self):
        return f"MetricObject({self.metric})"

    def to_dict(self) -> Dict:
        return {
            "metric": self.metric.to_dict(),
            "label": [label.to_dict() for label in self.label],
            "run_suuid": self.run_suuid,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "MetricObject":
        return cls(
            metric=Metric(
                name=data["metric"]["name"],
                value=data["metric"]["value"],
                type=data["metric"]["type"],
            ),
            label=[Label(**label) for label in data["label"]],
            run_suuid=data["run_suuid"],
            created_at=dateutil_parser.isoparse(data["created_at"]),
        )


@dataclass
class MetricList:
    metrics: List[MetricObject] = field(default_factory=list)

    def __len__(self):
        return len(self.metrics)

    def __iter__(self):
        yield from self.metrics

    def __getitem__(self, row):
        return self.metrics[row]

    def __str__(self):
        return f"List of {len(self.metrics)} metric" + ("s" if len(self.metrics) != 1 else "")

    def __repr__(self):
        return f"MetricList({len(self.metrics)} metric" + ("s" if len(self.metrics) != 1 else "") + ")"

    def append(self, metric: MetricObject):
        self.metrics.append(metric)

    def get(self, name) -> Union[MetricObject, None]:
        metrics_filtered = self.filter(name)
        if len(metrics_filtered) == 1:
            return metrics_filtered[0]
        if len(metrics_filtered) > 1:
            raise MultipleObjectsReturnedError(
                f"Found multiple metrics matching name '{name}', please use the method .filter(name=\"{name}\")."
            )
        return None

    def filter(self, name) -> List[MetricObject]:
        metrics_filtered = list(filter(lambda x: x.metric.name == name, self.metrics))
        return metrics_filtered

    def to_dict(self) -> List[dict]:
        return [metric.to_dict() for metric in self.metrics]

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=json_serializer)


@dataclass
class Run:
    suuid: str
    name: str
    description: str

    status: STATUS
    duration: int

    trigger: TRIGGER
    created_by: CreatedByWithAvatarRelation

    package: dict
    payload: Optional[PayloadRelation]
    result: dict
    artifact: dict
    metrics_meta: dict
    variables_meta: dict
    log: dict
    environment: dict

    job: JobRelation
    project: ProjectRelation
    workspace: WorkspaceRelation

    created_at: datetime.datetime
    modified_at: datetime.datetime
    started_at: Optional[datetime.datetime] = None
    finished_at: Optional[datetime.datetime] = None

    metrics: Optional[MetricList] = None
    variables: Optional[VariableList] = None

    def __str__(self):
        summary = {
            "suuid": self.suuid,
            "name": self.name,
            "status": self.status,
            "duration": self.duration,
            "result": self.result,
            "metrics": self.metrics_meta.get("count", 0),
            "variables": self.variables_meta.get("count", 0),
        }

        return f"Run summary: {summary}"

    def __repr__(self):
        return f"Run(suuid='{self.suuid}', status='{self.status}')"

    @classmethod
    def from_dict(cls, data: Dict) -> "Run":
        data["created_at"] = dateutil_parser.parse(data["created_at"])
        data["modified_at"] = dateutil_parser.parse(data["modified_at"])

        if data["started_at"]:
            data["started_at"] = dateutil_parser.parse(data["started_at"])
        if data["finished_at"]:
            data["finished_at"] = dateutil_parser.parse(data["finished_at"])

        created_by = CreatedByWithAvatarRelation.from_dict(data["created_by"])
        del data["created_by"]
        payload = PayloadRelation.from_dict(data["payload"]) if data["payload"] else None
        del data["payload"]
        job = JobRelation.from_dict(data["job"])
        del data["job"]
        project = ProjectRelation.from_dict(data["project"])
        del data["project"]
        workspace = WorkspaceRelation.from_dict(data["workspace"])
        del data["workspace"]

        return cls(created_by=created_by, payload=payload, job=job, project=project, workspace=workspace, **data)


@dataclass
class RunStatus:
    suuid: str
    status: STATUS
    name: str
    next_url: str
    created_by: CreatedByRelation
    job: JobRelation
    project: ProjectRelation
    workspace: WorkspaceRelation
    created_at: datetime.datetime
    modified_at: datetime.datetime
    started_at: Optional[datetime.datetime] = None
    finished_at: Optional[datetime.datetime] = None
    duration: int = 0

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.suuid}): {self.status}"
        return f"Run {self.suuid}: {self.status}"

    def __repr__(self):
        return f"RunStatus(suuid='{self.suuid}', status='{self.status}')"

    @classmethod
    def from_dict(cls, data: Dict) -> "RunStatus":
        data["created_at"] = dateutil_parser.isoparse(data["created_at"])
        data["modified_at"] = dateutil_parser.isoparse(data["modified_at"])

        if "started_at" in data and data["started_at"]:
            data["started_at"] = dateutil_parser.isoparse(data["started_at"])
        if "finished_at" in data and data["finished_at"]:
            data["finished_at"] = dateutil_parser.isoparse(data["finished_at"])

        created_by = CreatedByRelation.from_dict(data["created_by"])
        del data["created_by"]
        job = JobRelation.from_dict(data["job"])
        del data["job"]
        project = ProjectRelation.from_dict(data["project"])
        del data["project"]
        workspace = WorkspaceRelation.from_dict(data["workspace"])
        del data["workspace"]

        return cls(created_by=created_by, job=job, project=project, workspace=workspace, **data)


@dataclass
class ArtifactFile:
    name: str
    type: str
    size: int
    path: str
    parent: str
    last_modified: datetime.datetime

    @classmethod
    def from_dict(cls, data: Dict) -> "ArtifactFile":
        data["last_modified"] = dateutil_parser.isoparse(data["last_modified"])
        return cls(**data)


@dataclass
class ArtifactFileList:
    files: List[ArtifactFile] = field(default_factory=list)

    def __len__(self):
        return len(self.files)

    def __iter__(self):
        yield from self.files

    def __getitem__(self, row):
        return self.files[row]

    def __str__(self):
        return f"List of {len(self.files)} item" + ("s" if len(self.files) != 1 else "")

    def __repr__(self):
        return f"ArtifactFileList({len(self.files)} item" + ("s" if len(self.files) != 1 else "") + ")"


@dataclass
class ArtifactInfo:
    suuid: str

    size: int
    count_dir: int
    count_files: int

    run: RunRelation
    job: JobRelation
    project: ProjectRelation
    workspace: WorkspaceRelation

    created_at: datetime.datetime
    modified_at: datetime.datetime

    cdn_base_url: str
    files: ArtifactFileList

    @classmethod
    def from_dict(cls, data: Dict) -> "ArtifactInfo":
        data["created_at"] = dateutil_parser.isoparse(data["created_at"])
        data["modified_at"] = dateutil_parser.isoparse(data["modified_at"])

        data["files"] = ArtifactFileList(
            [ArtifactFile.from_dict(f) for f in data["files"]],
        )

        run = RunRelation.from_dict(data["run"])
        del data["run"]
        job = JobRelation.from_dict(data["job"])
        del data["job"]
        project = ProjectRelation.from_dict(data["project"])
        del data["project"]
        workspace = WorkspaceRelation.from_dict(data["workspace"])
        del data["workspace"]

        return cls(run=run, job=job, project=project, workspace=workspace, **data)
