# -*- coding: utf-8 -*-

"""Top-level package for askanna"""

__author__ = """AskAnna"""
__email__ = "devops@askanna.io"
__version__ = "0.7.0"


try:
    from appdirs import AppDirs  # noqa
except Exception as e:
    # we are propably within an installation
    print(e)
else:
    from .init import *  # noqa
