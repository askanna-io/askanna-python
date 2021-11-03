from dataclasses import dataclass
import json
import os
import sys
import tempfile
from typing import Any, List
import uuid

import click
from dateutil import parser as dateutil_parser

from askanna.core import exceptions
from askanna.core.apiclient import client
from askanna.core.dataclasses import Metric, MetricDataPair, MetricLabel
from askanna.core.utils import (
    create_suuid,
    json_serializer,
    labels_to_type,
    prepare_and_validate_value,
    translate_dtype,
)

__all__ = ["track_metric", "track_metrics", "MetricCollector", "MetricGateway"]

"""
How to use metrics module:

from askanna.core.metrics import *

mc = MetricCollector()
mc.add(metric=Metric(metric=MetricDataPair(name="foo", value=1, dtype="int"), label=[]))

# get json:

mc.to_json()
"""


class MetricsQuerySet:
    metrics = []
    queries = []
    parent = None

    def __init__(self, metrics: list = [], queries: list = [], parent=None):
        self.metrics = metrics
        self.queries = queries
        self.parent = parent

    def __len__(self):
        return len(self.metrics)

    def __iter__(self):
        yield from self.metrics

    def get(self, name, **kwargs):
        ret = self.filter(name, **kwargs)
        if len(ret) == 1:
            return ret[0]
        elif len(ret) > 1:
            click.echo(
                f"Found more metrics matching name '{name}',"
                f" use .filter(name='{name}') to get all matches.",
                err=True,
            )
            return ret[0]
        else:
            click.echo(f"A metric with name '{name}' is not found")

    def filter(self, name, **kwargs):
        ret = list(
            filter(lambda x: x.get("metric", {}).get("name") == name, self.metrics)
        )
        return ret

    def to_json(self) -> str:
        return json.dumps(self.metrics, indent=1)

    def to_raw(self) -> list:
        return self.metrics


@dataclass
class MetricCollector:
    metrics = []
    run_suuid: str = None
    local_suuid: str = None
    metrics_folder: str = None
    metrics_file: str = None
    changed: bool = False

    def __post_init__(self):
        if not self.run_suuid:
            # generate local suuid
            local_uuid = uuid.uuid4()
            self.local_suuid = create_suuid(local_uuid)

        self.metrics_folder = self.get_metrics_filepath()
        self.metrics_file = os.path.join(self.metrics_folder, "metrics.json")

        if self.run_suuid:
            self.restore_session()

    def get_suuid(self):
        """
        Return the run_suuid if exist, otherwise the local_suuid
        """
        return self.run_suuid or self.local_suuid

    def get_metrics_filepath(self):
        tmpdir = tempfile.gettempdir()
        return os.path.join(tmpdir, "askanna", "run", self.get_suuid())

    def metric_to_type(self, metric: dict = None) -> MetricDataPair:
        return MetricDataPair(
            name=metric["name"], value=metric["value"], dtype=metric["type"]
        )

    def label_to_type(self, label_list: list = None) -> list:
        _ret = []
        for label in label_list:
            _ret.append(
                MetricLabel(
                    name=label["name"], value=label["value"], dtype=label["type"]
                )
            )
        return _ret

    def restore_session(self):
        """
        We can only restore a session when the self.run_uuid is set
        """
        if not self.run_suuid:
            return

        restored_metrics = []
        try:
            with open(self.metrics_file, "r") as f:
                stored_metrics = json.load(f)
                for stored_metric in stored_metrics:
                    restored_metrics.append(
                        Metric(
                            metric=self.metric_to_type(stored_metric.get("metric")),
                            label=self.label_to_type(stored_metric.get("label")),
                            run_suuid=stored_metric.get("run_suuid"),
                            created=dateutil_parser.isoparse(
                                stored_metric.get("created")
                            ),
                        )
                    )

                self.metrics = restored_metrics
                del restored_metrics
        except FileNotFoundError:
            pass

    def save_session(self):
        # create folder for this session, name is the run_suuid with prefix askanna-metrics

        os.makedirs(self.metrics_folder, exist_ok=True)
        with open(self.metrics_file, "w") as f:
            f.write(self.to_json())

    def has_metrics(self) -> bool:
        return len(self.metrics) > 0

    def add(self, metric: Metric) -> None:
        metric.run_suuid = self.get_suuid()
        self.metrics.append(metric)
        self.save_session()
        self.changed = True

    def to_dict(self, yes=True) -> List:
        return [m.to_dict() for m in self.metrics]

    def to_json(self, yes=True) -> str:
        """
        We serialize all metrics to json for reporting or sending to AskAnna
        """
        return json.dumps(self.to_dict(), default=json_serializer)

    def save(self, run_suuid: str = None, force: bool = False) -> None:
        """
        Connect to AskAnna backend to save the metrics
        We will only attempt to submit if there is data recorded
        """
        if not self.changed and not force:
            # We will not save when there is nothing changed (e.g. no new metric added)
            return
        if len(self.to_dict()) and not run_suuid and not self.run_suuid:
            click.echo(
                "The run SUUID is not set for this session.\n"
                + "AskAnna cannot submit the metrics to the platform.",
                err=True,
            )
            click.echo(
                f"Your metrics are saved locally in:\n{self.metrics_file}", err=True
            )
            sys.exit(1)
        self.save_session()
        mgw = MetricGateway()
        # the run_suuid takes higher prio then the one set in init
        short_uuid = run_suuid or self.run_suuid
        mgw.change(short_uuid=short_uuid, metrics=self.to_dict())


# Start logic for metric collection
mc = MetricCollector(run_suuid=os.getenv("AA_RUN_SUUID"))


def track_metric(name: str, value: Any, label: dict = None) -> None:
    # store the metric
    if value:
        value, valid = prepare_and_validate_value(value)
        if not valid:
            click.echo(
                f"AskAnna cannot store this datatype. Metric not stored for {name}, {value}, {label}.",
                err=True
            )
            return
    # add value to track queue
    if value:
        datapair = MetricDataPair(name=name, value=value, dtype=translate_dtype(value))
    else:
        datapair = MetricDataPair(name=name, value=None, dtype="tag")
    labels = labels_to_type(label, labelclass=MetricLabel)

    metric = Metric(metric=datapair, label=labels)
    mc.add(metric)


def track_metrics(metrics: dict, label: dict = None) -> None:
    """
    Transform many metrics to internal format
    """
    for name, value in metrics.items():
        track_metric(name, value, label)


class MetricGateway:
    def __init__(self, *args, **kwargs):
        self.client = client

    def get(self, run: str = None, job: str = None) -> MetricsQuerySet:
        """
        Depending on what we get as argument, we call the 'list' function
        with specific query params for a different endpoint
        """

        if not any([run, job]):
            # we try to get local metrics if this exists

            if mc.run_suuid and mc.has_metrics():
                return MetricsQuerySet(metrics=mc.to_dict())
            elif mc.run_suuid:
                # RUN_SUUID is set but we don't have metrics
                return MetricsQuerySet(metrics=[])
            else:
                click.echo(
                    "We cannot find a run metric file for the active run.", err=True
                )
        else:
            pre_query_params = {
                "run_suuid": run,
                "job_suuid": job,
            }
            # filter out the none's:
            query_params = dict(
                filter(lambda x: x[1] is not None, pre_query_params.items())
            )
            return self.list(query_params=query_params)

    def list(self, query_params: dict = None) -> MetricsQuerySet:
        """
        List endpoint order:
        - job
        - run
        """

        endpoints = {
            "job": lambda x: "{}job/{}/metrics/".format(self.client.base_url, x),
            "run": lambda x: "{}runinfo/{}/metrics/".format(self.client.base_url, x),
        }
        if "run_suuid" in query_params.keys():
            url = endpoints.get("run")(query_params.get("run_suuid"))
        elif "job_suuid" in query_params.keys():
            url = endpoints.get("job")(query_params.get("job_suuid"))

        r = self.client.get(url, params=query_params)
        return MetricsQuerySet(metrics=r.json())

    def change(self, short_uuid, metrics):
        url = "{}{}/{}/{}/{}/".format(
            self.client.base_url, "runinfo", short_uuid, "metrics", short_uuid
        )

        r = self.client.put(url, json={"metrics": metrics})

        if r.status_code != 200:
            raise exceptions.GetError(
                "{} - Something went wrong while updating metrics "
                ": {}".format(r.status_code, r.json())
            )


# code for exiting in ipython from https://stackoverflow.com/a/40222538
# exit_register runs at the end of ipython %run or the end of the python interpreter
try:

    def exit_register(fun, *args, **kwargs):
        """Decorator that registers at post_execute. After its execution it
        unregisters itself for subsequent runs."""

        def callback():
            fun()
            ip.events.unregister("post_execute", callback)

        ip.events.register("post_execute", callback)

    ip = get_ipython()
except NameError:
    from atexit import register as exit_register


@exit_register
def handle_exit_save_metrics():
    try:
        if mc.has_metrics():
            mc.save()
    except Exception as e:
        # do a hard exit
        click.echo(f"Exit error in AskAnna SDK. {e}", err=True)
        os._exit(1)
