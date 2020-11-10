# -*- coding: utf-8 -*-
from __future__ import absolute_import
"""Allow askanna.cli to be executable through `python -m askanna.cli`"""

from .tool import cli


if __name__ == "__main__":
    cli()
