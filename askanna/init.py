# This file contains anything that needs to be loaded for `import askanna`. We separated this file to avoid conflicts
# while in installation mode

# Please note: never do `import askanna` here, this will cause an recursive import loop

import click

from askanna import USING_ASKANNA_CLI
from askanna.core.config import Config
from askanna.core.job import JobGateway
from askanna.core.metrics import track_metric, track_metrics, MetricGateway  # noqa
from askanna.core.variables_tracked import track_variable, track_variables  # noqa
from askanna.core.project import ProjectGateway
from askanna.core.result import ResultGateway
from askanna.core.run import RunMultipleQueryGateway, RunActionGateway
from askanna.core.utils import update_available
from askanna.core.workspace import WorkspaceGateway


if USING_ASKANNA_CLI:
    try:
        update_available()
    except Exception as e:
        click.echo(f"Something went wrong while checking if an update is available: {e}", err=True)

config = Config()

# Instantiated objects for query or actions, these do not contain any data on load and will be filled with data on
# using detail/get/list actions from it.
job = JobGateway()
metrics = MetricGateway()
project = ProjectGateway()
result = ResultGateway()
run = RunActionGateway()
runs = RunMultipleQueryGateway()
workspace = WorkspaceGateway()
