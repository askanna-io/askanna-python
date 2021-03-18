# this file contains anything that needs to be loaded for: `import askanna`
# we separated this file to avoid conflicts while in installation mode

# please note: never do `import asknna` here, this will cause an recursive import loop

from appdirs import AppDirs

from askanna.core.metrics import track_metric, track_metrics  # noqa
from askanna.core.metrics import MetricGateway
from askanna.core.run import RunMultipleQueryGateway, RunActionGateway

appname = "askanna"
appauthor = "askanna"
config_dirs = AppDirs(appname, appauthor)

# instantiated objects for query, these do not contain any data on load and will
# be filled with data on using detail/get/list actions from it.
metrics = MetricGateway()
run = RunActionGateway()
runs = RunMultipleQueryGateway()
