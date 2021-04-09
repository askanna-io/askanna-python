# this file contains anything that needs to be loaded for: `import askanna`
# we separated this file to avoid conflicts while in installation mode

# please note: never do `import asknna` here, this will cause an recursive import loop

from appdirs import AppDirs

from askanna.core.job import JobGateway
from askanna.core.metrics import track_metric, track_metrics, MetricGateway  # noqa
from askanna.core.variables_tracked import track_variable, track_variables  # noqa
from askanna.core.project import ProjectGateway

from askanna.core.run import RunMultipleQueryGateway, RunActionGateway
from askanna.core.workspace import WorkspaceGateway


appname = "askanna"
appauthor = "askanna"
config_dirs = AppDirs(appname, appauthor)

# instantiated objects for query or actions, these do not contain any data on load and will be filled with data on
# using detail/get/list actions from it.
job = JobGateway()
metrics = MetricGateway()
project = ProjectGateway()
run = RunActionGateway()
runs = RunMultipleQueryGateway()
workspace = WorkspaceGateway()
