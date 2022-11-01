import datetime
import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from dateutil import parser as dateutil_parser

from askanna.core.dataclasses.base import Label
from askanna.core.exceptions import MultipleObjectsReturned
from askanna.core.utils.object import json_serializer


@dataclass
class Payload:
    uuid: uuid.UUID
    short_uuid: str
    size: int
    lines: int
    created: datetime.datetime
    modified: datetime.datetime
    deleted: Optional[datetime.datetime] = None

    def __str__(self):
        return (
            f"Payload: {self.short_uuid} ({self.size} byte"
            + ("s" if self.size != 1 else "")
            + f" & {self.lines} line"
            + ("s" if self.lines != 1 else "")
            + ")"
        )

    def __repr__(self):
        return f"Payload(short_uuid='{self.short_uuid}', size={self.size}, lines={self.lines})"

    @classmethod
    def from_dict(cls, data: Dict) -> "Payload":
        data["uuid"] = uuid.UUID(data["uuid"])

        data["created"] = dateutil_parser.parse(data["created"])
        data["modified"] = dateutil_parser.parse(data["modified"])
        if data["deleted"]:
            data["deleted"] = dateutil_parser.parse(data["deleted"])

        return cls(**data)


@dataclass
class PayloadRelation:
    uuid: uuid.UUID
    short_uuid: str
    name: str
    size: int
    lines: int

    @classmethod
    def from_dict(cls, data: Dict) -> "PayloadRelation":
        del data["relation"]
        data["uuid"] = uuid.UUID(data["uuid"])

        return cls(**data)


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
    created: Optional[datetime.datetime] = None

    def __post_init__(self):
        if not self.created:
            # The created time is set with timezome set to UTC so that we don't have to figure out what the local
            # timezone is. UTC is the default timezone for the API.
            self.created = datetime.datetime.now(datetime.timezone.utc)

    def __str__(self):
        return f"{self.variable} ({len(self.label)} label" + ("s" if len(self.label) != 1 else "") + ")"

    def __repr__(self):
        return f"VariableObject({self.variable})"

    def to_dict(self) -> Dict:
        return {
            "variable": self.variable.to_dict(),
            "label": [label.to_dict() for label in self.label],
            "run_suuid": self.run_suuid,
            "created": self.created,
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
            created=dateutil_parser.isoparse(data["created"]),
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
            raise MultipleObjectsReturned(
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
    created: Optional[datetime.datetime] = None

    def __post_init__(self):
        if not self.created:
            # The created time is set with timezome set to UTC so that we don't have to figure out what the local
            # timezone is. UTC is the default timezone for the API.
            self.created = datetime.datetime.now(datetime.timezone.utc)

    def __str__(self):
        return f"{self.metric} ({len(self.label)} label" + ("s" if len(self.label) != 1 else "") + ")"

    def __repr__(self):
        return f"MetricObject({self.metric})"

    def to_dict(self) -> Dict:
        return {
            "metric": self.metric.to_dict(),
            "label": [label.to_dict() for label in self.label],
            "run_suuid": self.run_suuid,
            "created": self.created,
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
            created=dateutil_parser.isoparse(data["created"]),
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
            raise MultipleObjectsReturned(
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
    uuid: uuid.UUID
    short_uuid: str
    name: str
    description: str

    status: str
    duration: int

    trigger: dict
    created_by: dict

    package: dict
    payload: Optional[PayloadRelation]
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
    started: Optional[datetime.datetime] = None
    finished: Optional[datetime.datetime] = None

    metrics: Optional[MetricList] = None
    variables: Optional[VariableList] = None

    def __str__(self):
        summary = {
            "short_uuid": self.short_uuid,
            "name": self.name,
            "status": self.status,
            "duration": self.duration,
            "result": self.result,
            "metrics": self.metrics_meta.get("count", 0),
            "variables": self.variables_meta.get("count", 0),
        }

        return f"Run summary: {summary}"

    def __repr__(self):
        return f"Run(short_uuid='{self.short_uuid}', status='{self.status}')"

    @classmethod
    def from_dict(cls, data: Dict) -> "Run":
        payload = PayloadRelation.from_dict(data["payload"]) if data["payload"] else None
        del data["payload"]
        return cls(payload=payload, **data)


@dataclass
class RunList:
    runs: List[Run] = field(default_factory=list)

    def __len__(self):
        return len(self.runs)

    def __iter__(self):
        yield from self.runs

    def __getitem__(self, row):
        return self.runs[row]

    def __str__(self):
        return f"List of {len(self.runs)} run" + ("s" if len(self.runs) != 1 else "")

    def __repr__(self):
        return f"RunList({len(self.runs)} run" + ("s" if len(self.runs) != 1 else "") + ")"


@dataclass
class RunStatus:
    uuid: uuid.UUID
    short_uuid: str
    status: str
    name: str
    next_url: str
    job: dict
    workspace: dict
    project: dict
    created: datetime.datetime
    updated: datetime.datetime
    finished: Optional[datetime.datetime] = None
    duration: int = 0

    def __str__(self):
        if self.name:
            return f"{self.name} ({self.short_uuid}): {self.status}"
        return f"{self.short_uuid}: {self.status}"

    def __repr__(self):
        return f"RunStatus(suuid={self.short_uuid}, status={self.status})"

    @classmethod
    def from_dict(cls, data: Dict) -> "RunStatus":
        del data["message_type"]

        data["uuid"] = uuid.UUID(data["uuid"])
        data["created"] = dateutil_parser.isoparse(data["created"])
        data["updated"] = dateutil_parser.isoparse(data["updated"])
        if "finished" in data and data["finished"]:
            data["finished"] = dateutil_parser.isoparse(data["finished"])

        return cls(**data)


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
    run: uuid.UUID
    uuid: uuid.UUID
    short_uuid: str

    size: int
    count_dir: int
    count_files: int

    files: ArtifactFileList
    cdn_base_url: str

    created: datetime.datetime
    modified: datetime.datetime
    deleted: Optional[datetime.datetime] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "ArtifactInfo":
        data["run"] = uuid.UUID(data["run"])
        data["uuid"] = uuid.UUID(data["uuid"])
        data["created"] = dateutil_parser.isoparse(data["created"])
        data["modified"] = dateutil_parser.isoparse(data["modified"])
        if "deleted" in data and data["deleted"]:
            data["deleted"] = dateutil_parser.isoparse(data["deleted"])

        data["files"] = ArtifactFileList(
            [ArtifactFile.from_dict(f) for f in data["files"]],
        )

        return cls(**data)
