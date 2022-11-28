from __future__ import absolute_import

import importlib

import click

from askanna import __version__ as askanna_version

HELP = """
The run util is used to support AskAnna runs
"""

SHORT_HELP = "AskAnna Run Utils"

EPILOG = """
For usage and help on a specific command, run it with a --help flag, e.g.:

    askanna-run-utils [COMMAND] --help
"""


@click.group(
    help=HELP,
    short_help=SHORT_HELP,
    epilog=EPILOG,
)
@click.version_option(version=askanna_version, prog_name="AskAnna Run Utils")
def cli():
    """
    Initialize the AskAnna Run Utils commands
    """


commands = [
    "push_artifact",
    "push_metrics",
    "push_result",
    "push_variables",
    "get_package",
    "get_payload",
    "get_run_manifest",
]

for command in commands:
    module_path = "askanna.cli.run_utils." + command
    command_module = importlib.import_module(module_path)
    command_name = command.replace("_", "-")
    cli.add_command(command_module.cli, command_name)
