import json
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Union

import click

from askanna.core.dataclasses.run import (
    MetricList,
    MetricObject,
    VariableList,
    VariableObject,
)
from askanna.core.utils.suuid import create_suuid
from askanna.gateways.run import RunGateway


class CollectorTemplate:
    """
    Base class for collectors
    """

    # To use the CollectorTemplate, you need to create a class that inherits from it. This class needs to implement the
    # following attributes:
    # - collector_type
    # - file_name

    # property:
    # - data_collection

    # And methods:
    # - append_from_dict (with one input attribute of type dict)
    # - save_to_askanna

    collector_type = "template"
    file_name = "collector.json"

    def __init__(self, run_suuid: Optional[str] = None):
        if self.collector_type == "template":
            assert self.collector_type != "template", (
                "CollectorTemplate is an abstract base class. You should subclass it and set 'collector_type' to "
                "a value that is not 'template'."
            )

        self.run_suuid = run_suuid
        if not self.run_suuid:
            self.local_suuid = create_suuid(uuid.uuid4())

        self.collector_file = Path(tempfile.gettempdir(), "askanna/run", self.suuid, self.file_name)

        if self.run_suuid:
            self._restore_session()

        self.changed = False

    @property
    def data_collection(self):
        raise NotImplementedError(f"Please implement 'data_collection' for  {self.__class__.__name__}")

    def append_from_dict(self, *args) -> None:
        raise NotImplementedError(f"Please implement 'append_from_dict' for  {self.__class__.__name__}")

    def save_to_askanna(self):
        raise NotImplementedError(f"Please implement 'save_to_askanna' for  {self.__class__.__name__}")

    @property
    def suuid(self) -> str:
        """
        Return the run_suuid if exist, otherwise the local_suuid
        """
        return self.run_suuid or self.local_suuid

    def __len__(self) -> int:
        return len(self.data_collection)

    def add(self, object: Union[MetricObject, VariableObject]) -> None:
        if not object.run_suuid:
            object.run_suuid = self.suuid
        elif object.run_suuid != self.suuid:
            raise ValueError(
                f"The run SUUID '{object.run_suuid}' of the {self.collector_type} does not match the run SUUID "
                f"'{self.suuid}' of the session where the collector is initialized."
            )

        self.data_collection.append(object)
        self.save_local()
        self.changed = True

    def _restore_session(self):
        """
        Restore the run session and get records from the json collector file. The file does not have to exist, for
        example when the store is started for a new run.
        """
        try:
            with self.collector_file.open() as f:
                records = json.load(f)
                for record in records:
                    self.append_from_dict(record)
        except FileNotFoundError:
            pass

    def save_local(self):
        self.collector_file.parent.mkdir(parents=True, exist_ok=True)
        with self.collector_file.open("w") as f:
            f.write(self.data_collection.to_json())

    def save(self, force: bool = False) -> None:
        """
        Save the collected data in the AskAnna Backend. Only submit when data is changed or when force is set to True.
        """
        if not self.changed and not force:
            # We will not save when there is nothing changed
            return

        self.save_local()
        if len(self.data_collection.to_dict()) and not self.run_suuid:
            click.echo("The run SUUID is not set for this session. AskAnna cannot submit the data to the platform.")
            click.echo(f"Your {self.collector_type} data is saved locally in:\n  {self.collector_file}")
            return

        self.save_to_askanna()


class MetricCollector(CollectorTemplate):
    collector_type = "metric"
    file_name = "metrics.json"

    metrics = MetricList()

    @property
    def data_collection(self) -> MetricList:
        return self.metrics

    def append_from_dict(self, dict: dict) -> None:
        self.data_collection.append(MetricObject.from_dict(dict))

    def save_to_askanna(self):
        if self.run_suuid:
            RunGateway().metric_update(self.run_suuid, self.metrics)


class VariableCollector(CollectorTemplate):
    collector_type = "variable"
    file_name = "variables.json"

    variables = VariableList()

    @property
    def data_collection(self) -> VariableList:
        return self.variables

    def append_from_dict(self, dict: dict) -> None:
        self.data_collection.append(VariableObject.from_dict(dict))

    def save_to_askanna(self):
        if self.run_suuid:
            RunGateway().variable_update(self.run_suuid, self.variables)
