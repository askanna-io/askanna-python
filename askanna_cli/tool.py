# -*- coding: utf-8 -*-
from askanna_cli.utils import init_checks
from askanna_cli.utils import update_available
import askanna_cli
import click
import importlib
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


HELP = """
AskAnna CLI helps you running DSP
"""

SHORT_HELP = "AskAnna command-line client"

EPILOG = """
For usage and help on a specific command, run it with a --help flag, e.g.:

    askanna createproject --help
"""

CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}


@click.group(help=HELP, short_help=SHORT_HELP, epilog=EPILOG,
             context_settings=CONTEXT_SETTINGS)
@click.version_option(askanna_cli.__version__)
def cli():
    update_url = update_available()
    if update_url:
        click.echo("INFO: A newer version of askanna_cli is available. Update "
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
    module_path = "askanna_cli." + command
    command_module = importlib.import_module(module_path)
    command_name = command.replace('_', '-')
    cli.add_command(command_module.cli, command_name)


# perform initial checks on config and auth status
init_checks()
