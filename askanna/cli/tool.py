# -*- coding: utf-8 -*-
import importlib
import sys

from askanna import __version__ as askanna_version
import click


HELP = """
The AskAnna CLI helps you running data science projects on AskAnna.
"""

SHORT_HELP = "AskAnna CLI client"

EPILOG = """
For usage and help on a specific command, run it with a --help flag, e.g.:

    askanna login --help
"""

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def cli():
    """
    This is a wrapper to catch any command and errors
    """
    try:
        cli_commands()
    except Exception as e:
        click.echo(e, err=True)
        sys.exit(1)


@click.group(
    help=HELP, short_help=SHORT_HELP, epilog=EPILOG, context_settings=CONTEXT_SETTINGS
)
@click.version_option(version=askanna_version, prog_name="AskAnna CLI")
def cli_commands():
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
    cli_commands.add_command(command_module.cli, command_name)
