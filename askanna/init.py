"""This file contains anything that needs to be loaded for `import askanna` to work."""
import click

from askanna import USING_ASKANNA_CLI
from askanna.core.utils.main import update_available
from askanna.gateways.job import JobGateway
from askanna.gateways.project import ProjectGateway
from askanna.gateways.variable import VariableGateway
from askanna.gateways.workspace import WorkspaceGateway
from askanna.sdk.run import GetRunsSDK, ResultSDK, RunSDK
from askanna.sdk.track import (  # noqa: F401
    track_metric,
    track_metrics,
    track_variable,
    track_variables,
)

if USING_ASKANNA_CLI:
    try:
        update_available()
    except Exception as e:
        click.echo(f"Something went wrong while checking if an update is available: {e}", err=True)


# Instantiated objects for query or actions, these do not contain any data on load and will be filled when needed
job = JobGateway()
project = ProjectGateway()
result = ResultSDK()
run = RunSDK()
runs = GetRunsSDK()
variable = VariableGateway()
workspace = WorkspaceGateway()
