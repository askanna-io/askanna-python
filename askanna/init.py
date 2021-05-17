# This file contains anything that needs to be loaded for `import askanna`. We separated this file to avoid conflicts
# while in installation mode

# Please note: never do `import askanna` here, this will cause an recursive import loop

from askanna import USING_ASKANNA_CLI
from askanna.core.job import JobGateway
from askanna.core.metrics import track_metric, track_metrics, MetricGateway  # noqa
from askanna.core.variables_tracked import track_variable, track_variables  # noqa
from askanna.core.project import ProjectGateway
from askanna.core.utils import update_available
from askanna.core.run import RunMultipleQueryGateway, RunActionGateway
from askanna.core.workspace import WorkspaceGateway


if USING_ASKANNA_CLI:
    update_available()

# Instantiated objects for query or actions, these do not contain any data on load and will be filled with data on
# using detail/get/list actions from it.
job = JobGateway()
metrics = MetricGateway()
project = ProjectGateway()
run = RunActionGateway()
runs = RunMultipleQueryGateway()
workspace = WorkspaceGateway()
