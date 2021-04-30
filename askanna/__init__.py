# -*- coding: utf-8 -*-

"""Top-level package for askanna"""

__author__ = """AskAnna"""
__email__ = "devops@askanna.io"
__version__ = "0.8.0"

import sys

# determine whether we are in the CLI or using the SDK
USING_ASKANNA_CLI = any([sys.argv[0].endswith("bin/askanna")])

try:
    from appdirs import AppDirs  # noqa
except Exception as e:
    # we are propably within an installation
    print(e)
else:
    from .init import *  # noqa
