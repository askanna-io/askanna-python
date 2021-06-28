# -*- coding: utf-8 -*-
from __future__ import absolute_import

"""Allow askanna.cli.run_utils to be executable through `python -m askanna.cli.run_utils`"""

from .tool import cli


if __name__ == "__main__":

    cli()
