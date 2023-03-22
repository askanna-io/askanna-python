import importlib

import click

from askanna import ASKANNA_VERSION

HELP = """
The AskAnna CLI helps you running data science projects on AskAnna.
"""

SHORT_HELP = "AskAnna CLI"

EPILOG = """
For usage and help on a specific command, run it with a --help flag, e.g.:

    askanna [COMMAMD] --help
"""


@click.group(
    help=HELP,
    short_help=SHORT_HELP,
    epilog=EPILOG,
)
@click.version_option(version=ASKANNA_VERSION, prog_name="AskAnna CLI")
def cli():
    """
    Initialize the AskAnna CLI commands
    """


commands = [
    "artifact",
    "create",
    "init",
    "job",
    "login",
    "logout",
    "project",
    "push",
    "result",
    "run",
    "variable",
    "workspace",
]

for command in commands:
    module_path = "askanna.cli." + command
    command_module = importlib.import_module(module_path)
    command_name = command.replace("_", "-")
    cli.add_command(command_module.cli, command_name)
