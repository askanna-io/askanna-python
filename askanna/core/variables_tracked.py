"""
Management of tracking variables in AskAnna
This is the class which act as gateway to the API of AskAnna
"""
from dataclasses import dataclass
import json
import os
import sys
import tempfile
from typing import List
import uuid

import click
from dateutil import parser as dateutil_parser

from askanna.core import client, exceptions
from askanna.core.dataclasses import VariableTracked, VariableDataPair, VariableLabel
from askanna.core.utils import (
    create_suuid,
    json_serializer,
    translate_dtype,
    validate_value,
    labels_to_type,
)

__all__ = [
    "track_variable",
    "track_variables",
    "VariableCollector",
    "VariableTrackedGateway",
]


class VariablesQuerySet:
    variables = []
    queries = []
    parent = None

    def __init__(self, variables: list = [], queries: list = [], parent=None):
        self.variables = variables
        self.queries = queries
        self.parent = parent

    def __len__(self):
        return len(self.variables)

    def __iter__(self):
        yield from self.variables

    def get(self, name, **kwargs):
        ret = self.filter(name, **kwargs)
        if len(ret) == 1:
            return ret[0]
        elif len(ret) > 1:
            click.echo(
                f"Found more variables matching name '{name}',"
                f" use .filter(name='{name}') to get all matches.",
                err=True,
            )
            return ret[0]
        else:
            click.echo(f"A variable with name '{name}' is not found")

    def filter(self, name, **kwargs):
        ret = list(
            filter(lambda x: x.get("variable", {}).get("name") == name, self.variables)
        )
        return ret

    def to_json(self) -> str:
        return json.dumps(self.variables, indent=1)

    def to_raw(self) -> list:
        return self.variables


class VariableTrackedGateway:
    def __init__(self, *args, **kwargs):
        self.client = client

    def change(self, short_uuid, variables):
        url = "{}{}/{}/{}/{}/".format(
            self.client.config.remote, "runinfo", short_uuid, "variables", short_uuid
        )

        r = self.client.patch(url, json={"variables": variables})

        if r.status_code != 200:
            raise exceptions.GetError(
                "{} - Something went wrong while updating variables "
                ": {}".format(r.status_code, r.json())
            )

    def get(self, run: str = None, job: str = None) -> VariablesQuerySet:
        """
        Depending on what we get as argument, we call the 'list' function
        with specific query params for a different endpoint
        """

        if not any([run, job]):
            # we try to get local variables if this exists

            if vc.run_suuid and vc.has_variables():
                return VariablesQuerySet(variables=vc.to_dict())
            elif vc.run_suuid:
                # RUN_SUUID is set but we don't have variables
                return VariablesQuerySet(variables=[])
            else:
                click.echo(
                    "We cannot find a run variables file for the active run.", err=True
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

    def list(self, query_params: dict = None) -> VariablesQuerySet:
        """
        List endpoint order:
        - job
        - run
        """

        endpoints = {
            "job": lambda x: "{}job/{}/variables_tracked/".format(
                self.client.config.remote, x
            ),
            "run": lambda x: "{}runinfo/{}/variables/".format(
                self.client.config.remote, x
            ),
        }
        if "run_suuid" in query_params.keys():
            url = endpoints.get("run")(query_params.get("run_suuid"))
        elif "job_suuid" in query_params.keys():
            url = endpoints.get("job")(query_params.get("job_suuid"))

        r = self.client.get(url, params=query_params)
        return VariablesQuerySet(variables=r.json())


def track_variable(name: str, value, label: dict = None) -> None:
    # store the variable
    if value and not validate_value(value):
        click.echo(
            f"AskAnna cannot store this datatype. Variable not stored for {name}, {value}, {label}.",
            err=True
        )
        return

    # we don't want to store secrets, so filter them and replace value if it is sensitive information
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

    # add value to track queue
    if value:
        datapair = VariableDataPair(name=name, value=value, dtype=translate_dtype(value))
    else:
        datapair = VariableDataPair(name=name, value=None, dtype="tag")
    labels = [
        VariableLabel(name="source", value="run", dtype="string")
    ] + labels_to_type(label, labelclass=VariableLabel)

    if is_masked:
        labels.append(
            VariableLabel(**{"name": "is_masked", "value": None, "dtype": "tag"})
        )

    variable = VariableTracked(variable=datapair, label=labels)
    vc.add(variable)


def track_variables(variables: dict, label: dict = None) -> None:
    """
    Transform many variables to internal format
    """
    for name, value in variables.items():
        track_variable(name, value, label)


@dataclass
class VariableCollector:
    variables = []
    run_suuid: str = None
    local_suuid: str = None
    variables_folder: str = None
    variables_file: str = None
    changed: bool = False

    def __post_init__(self):
        if not self.run_suuid:
            # generate local suuid
            local_uuid = uuid.uuid4()
            self.local_suuid = create_suuid(local_uuid)

        self.variables_folder = self.get_variables_filepath()
        self.variables_file = os.path.join(self.variables_folder, "variables.json")

        if self.run_suuid:
            self.restore_session()

    def get_suuid(self):
        """
        Return the run_suuid if exist, otherwise the local_suuid
        """
        return self.run_suuid or self.local_suuid

    def get_variables_filepath(self):
        tmpdir = tempfile.gettempdir()
        return os.path.join(tmpdir, "askanna", "run", self.get_suuid())

    def variable_to_type(self, variable: dict = None) -> VariableDataPair:
        return VariableDataPair(
            name=variable["name"], value=variable["value"], dtype=variable["type"]
        )

    def label_to_type(self, label_list: list = None) -> list:
        _ret = []
        for label in label_list:
            _ret.append(
                VariableLabel(
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

        restored_variables = []
        try:
            with open(self.variables_file, "r") as f:
                stored_variables = json.load(f)
                for stored_variable in stored_variables:
                    restored_variables.append(
                        VariableTracked(
                            variable=self.variable_to_type(
                                stored_variable.get("variable")
                            ),
                            label=self.label_to_type(stored_variable.get("label")),
                            run_suuid=stored_variable.get("run_suuid"),
                            created=dateutil_parser.isoparse(
                                stored_variable.get("created")
                            ),
                        )
                    )

                self.variables = restored_variables
                del restored_variables
        except FileNotFoundError:
            pass

    def save_session(self):
        # create folder for this session, name is the run_suuid with prefix askanna-variables

        os.makedirs(self.variables_folder, exist_ok=True)
        with open(self.variables_file, "w") as f:
            f.write(self.to_json())

    def has_variables(self) -> bool:
        return len(self.variables) > 0

    def add(self, variable: VariableTracked) -> None:
        variable.run_suuid = self.get_suuid()
        self.variables.append(variable)
        self.save_session()
        self.changed = True

    def to_dict(self, yes=True) -> List:
        return [m.to_dict() for m in self.variables]

    def to_json(self, yes=True) -> str:
        """
        We serialize all variables to json for reporting or sending to AskAnna
        """
        return json.dumps(self.to_dict(), default=json_serializer)

    def save(self, run_suuid: str = None, force: bool = False) -> None:
        """
        Connect to the AskAnna backend to save the variables
        We will only attempt to submit if there is data recorded
        """
        if not self.changed and not force:
            # We will not save when there is nothing changed (e.g. no new variable added)
            return
        if len(self.to_dict()) and not run_suuid and not self.run_suuid:
            click.echo(
                "The run SUUID is not set for this session.\n"
                + "AskAnna cannot submit the variables to the platform.",
                err=True,
            )
            click.echo(
                f"Your variables are saved locally in:\n{self.variables_file}", err=True
            )
            sys.exit(1)
        self.save_session()
        mgw = VariableTrackedGateway()
        # the run_suuid takes higher prio then the one set in init
        short_uuid = run_suuid or self.run_suuid
        mgw.change(short_uuid=short_uuid, variables=self.to_dict())


# Start logic for variable collection
vc = VariableCollector(run_suuid=os.getenv("AA_RUN_SUUID"))


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
def handle_exit_save_variables():
    try:
        if vc.has_variables():
            vc.save()
    except Exception as e:
        # do a hard exit
        click.echo(f"Exit error in AskAnna SDK. {e}", err=True)
        os._exit(1)
