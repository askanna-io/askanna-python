# -*- coding: utf-8 -*-

"""Top-level package for askanna"""

__author__ = "AskAnna Team"
__email__ = "devops@askanna.io"
__version__ = "0.11.0"

import re
import sys

# Determine whether we are in the CLI or using the SDK
USING_ASKANNA_CLI : bool = any([re.match(".+bin/askanna*", sys.argv[0])])

try:
    import click  # noqa
except Exception as e:
    # We are propably within an installation
    print(e)
else:
    from .init import *  # noqa
