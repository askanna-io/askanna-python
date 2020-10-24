# -*- coding: utf-8 -*-

"""Top-level package for askanna-cli."""

__author__ = """Anthony Leung"""
__email__ = 'anthony@askanna.io'
__version__ = '0.3.1'

try:
    from appdirs import AppDirs
except Exception as e:
    # we are propably within an installation
    print(e)
else:
    appname = "askanna"
    appauthor = "askanna"
    config_dirs = AppDirs(appname, appauthor)
