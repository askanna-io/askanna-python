# -*- coding: utf-8 -*-
import importlib
import sys

from askanna import __version__ as askanna_version
import click

try:
    from dotenv import find_dotenv, load_dotenv
except ImportError:
    pass  # we only use dotenv for development
else:
    load_dotenv(find_dotenv())


HELP = """
The run util is used to support AskAnna runs
"""

SHORT_HELP = "AskAnna run util"

EPILOG = """
For usage and help on a specific command, run it with a --help flag, e.g.:

    askanna-run-utils get-payload --help
"""

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def cli():
    """
    This is a wrapper to catch any command and errors
    """
    try:
        cli_commands()
    except Exception as e:
        click.echo(e)
        sys.exit(1)


@click.group(
    help=HELP, short_help=SHORT_HELP, epilog=EPILOG, context_settings=CONTEXT_SETTINGS
)
@click.version_option(version=askanna_version, prog_name="AskAnna Run Utils")
def cli_commands():
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
    cli_commands.add_command(command_module.cli, command_name)
