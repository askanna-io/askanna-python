# -*- coding: utf-8 -*-
from askanna.cli.utils import init_checks
from askanna.cli.utils import update_available
import askanna
import click
import importlib
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


@click.group(help=HELP, short_help=SHORT_HELP, epilog=EPILOG,
             context_settings=CONTEXT_SETTINGS)
@click.version_option(askanna.__version__)
def cli():
    update_url = update_available()
    if update_url:
        click.echo("INFO: A newer version of AskAnna is available. Update "
                   "via pip or get it at {}".format(update_url), err=True)


commands = [
    "login",
    "logout",
    "init",
    "createproject",
    "payload",
    "push",
    "package_download",
    "jobrun_manifest",
    "artifact",
    "upload_result",
    "variable",
]

for command in commands:
    module_path = "askanna.cli." + command
    command_module = importlib.import_module(module_path)
    command_name = command.replace('_', '-')
    cli.add_command(command_module.cli, command_name)


# perform initial checks on config and auth status
init_checks()