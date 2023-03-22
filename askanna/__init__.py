"""
The AskAnna CLI & Python SDK is part of the AskAnna platform to kickstart your data science projects.
"""

__version__ = "0.23.0.dev2"

import re
import sys

ASKANNA_VERSION = __version__

# Determine whether we are in the CLI or using the SDK by chekiking for the `askanna` command
USING_ASKANNA_CLI: bool = any([re.match(".+bin/askanna$", sys.argv[0])])

try:
    import click  # noqa: F401
except ModuleNotFoundError as e:
    # We are propably within an installation for hatch or pip, skip the rest of the initialization
    print(e)
else:
    # We use dotenv for development but it's not a requirement for the CLI or SDK
    try:
        from dotenv import find_dotenv, load_dotenv
    except ImportError:
        pass
    else:
        load_dotenv(find_dotenv())

    # Initialize AskAnna after everything is loaded successfully
    from .init import *  # noqa
