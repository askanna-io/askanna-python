# -*- coding: utf-8 -*-
import importlib
import sys

import askanna
from askanna.core.utils import init_checks
from askanna.core.utils import update_available
import click
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


HELP = """
The AskAnna CLI helps you running data science projects on AskAnna.
"""

SHORT_HELP = "AskAnna CLI client"

EPILOG = """
For usage and help on a specific command, run it with a --help flag, e.g.:

    askanna login --help
"""

CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}


def cli():
    """
    This is a wrapper to catch any command and errors
    """
    try:
        cli_commands()
    except Exception as e:
        click.echo(e)
        sys.exit(1)


@click.group(help=HELP, short_help=SHORT_HELP, epilog=EPILOG,
             context_settings=CONTEXT_SETTINGS)
@click.version_option(askanna.__version__)
def cli_commands():
    update_url = update_available()
    if update_url:
        click.echo("INFO: A newer version of AskAnna is available. Update "
                   "via pip or get it at {}".format(update_url), err=True)


commands = [
    "login",
    "logout",
    "create",
    "init",
    "payload",
    "push",
    "package_download",
    "jobrun_manifest",
    "artifact",
    "upload_result",
    "variable",
    "run",
]

for command in commands:
    module_path = "askanna.cli." + command
    command_module = importlib.import_module(module_path)
    command_name = command.replace('_', '-')
    cli_commands.add_command(command_module.cli, command_name)


# perform initial checks on config and auth status
init_checks()
