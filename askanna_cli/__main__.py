# -*- coding: utf-8 -*-
from __future__ import absolute_import
"""Allow askanna_cli to be executable through `python -m askanna_cli`"""

from .tool import cli


if __name__ == "__main__":
    cli()
