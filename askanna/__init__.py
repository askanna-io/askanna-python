# -*- coding: utf-8 -*-

"""Top-level package for askanna"""

__author__ = """AskAnna"""
__email__ = "devops@askanna.io"
__version__ = "0.6.0"


try:
    from appdirs import AppDirs

except Exception as e:
    # we are propably within an installation
    print(e)
else:
    appname = "askanna"
    appauthor = "askanna"
    config_dirs = AppDirs(appname, appauthor)
