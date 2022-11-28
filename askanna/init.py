"""This file contains anything that needs to be loaded for `import askanna` to work."""
import click

from askanna import USING_ASKANNA_CLI
from askanna.core.utils.main import update_available
from askanna.sdk.job import JobSDK
from askanna.sdk.project import ProjectSDK
from askanna.sdk.run import GetRunsSDK, ResultSDK, RunSDK
from askanna.sdk.track import (  # noqa: F401
    track_metric,
    track_metrics,
    track_variable,
    track_variables,
)
from askanna.sdk.variable import VariableSDK
from askanna.sdk.workspace import WorkspaceSDK

if USING_ASKANNA_CLI:
    try:
        update_available()
    except Exception as e:
        click.echo(f"Something went wrong while checking if an update is available: {e}", err=True)


# Instantiated objects for query or actions, these do not contain any data on load and will be filled when needed
job = JobSDK()
project = ProjectSDK()
result = ResultSDK()
run = RunSDK()
runs = GetRunsSDK()
variable = VariableSDK()
workspace = WorkspaceSDK()
