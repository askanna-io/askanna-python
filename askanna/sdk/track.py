import os
from typing import Any, Optional, Union

import click

from askanna.core.collector import MetricCollector, VariableCollector
from askanna.core.dataclasses.base import Label
from askanna.core.dataclasses.run import Metric, MetricObject, Variable, VariableObject
from askanna.core.utils.at_exit import exit_register
from askanna.core.utils.main import make_label_list
from askanna.core.utils.object import (
    get_type,
    object_fullname,
    prepare_and_validate_value,
    value_not_empty,
)

__all__ = [
    "track_metric",
    "track_metrics",
    "track_variable",
    "track_variables",
]

# Start metric and variable collection for the current session and register save collections on exit
metric_collector = MetricCollector(run_suuid=os.getenv("AA_RUN_SUUID"))
variable_collector = VariableCollector(run_suuid=os.getenv("AA_RUN_SUUID"))


@exit_register
def at_exit_save_metrics():
    if len(metric_collector) > 0:
        metric_collector.save()
    if len(variable_collector) > 0:
        variable_collector.save()


def track_metric(name: str, value: Any = None, label: Optional[Union[str, list, dict]] = None) -> None:
    if value_not_empty(value):
        value, valid = prepare_and_validate_value(value)
        if not valid:
            click.echo(
                f"AskAnna cannot store the datatype '{object_fullname(value)}'. Metric not stored for '{name}' with "
                f"value '{value}' and labels '{label}'.",
                err=True,
            )
            return
        metric = Metric(name=name, value=value, type=get_type(value))
    else:
        metric = Metric(name=name, value=None, type="tag")

    # Add value to track queue
    metric_object = MetricObject(
        metric=metric,
        label=make_label_list(label) if label else [],
    )
    metric_collector.add(metric_object)


def track_metrics(metrics: dict, label: Optional[Union[str, list, dict]] = None) -> None:
    """
    Transform many metrics to individual metrics using track_metric
    """
    for name, value in metrics.items():
        track_metric(name, value, label)


def track_variable(name: str, value: Any = None, label: Optional[Union[str, list, dict]] = None) -> None:
    if value_not_empty(value):
        value, valid = prepare_and_validate_value(value)
        if not valid:
            click.echo(
                f"AskAnna cannot store the datatype '{object_fullname(value)}'. Variable not stored for '{name}' with "
                f"value '{value}' and labels '{label}'.",
                err=True,
            )
            return

    # We don't want to store secrets, so filter them and replace value if it is sensitive information
    variable_name = name.upper()
    is_masked = any(
        [
            "KEY" in variable_name,
            "TOKEN" in variable_name,
            "SECRET" in variable_name,
            "PASSWORD" in variable_name,
        ]
    )
    if is_masked:
        value = "***masked***"

    # Add value to track queue
    if value_not_empty(value):
        variable = Variable(name=name, value=value, type=get_type(value))
    else:
        variable = Variable(name=name, value=None, type="tag")

    labels = [Label(name="source", value="run", type="string")]
    if label:
        labels.extend(make_label_list(label))
    if is_masked:
        labels.append(Label(**{"name": "is_masked", "value": None, "type": "tag"}))

    variable = VariableObject(variable=variable, label=labels)
    variable_collector.add(variable)


def track_variables(variables: dict, label: Union[str, list, dict] = "") -> None:
    """
    Transform many variables to individual variables using track_variable
    """
    for name, value in variables.items():
        track_variable(name, value, label)
