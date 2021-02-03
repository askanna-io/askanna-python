import getpass
import sys

import click

from askanna.core import client as askanna_client
from askanna.core.auth import AuthGateway

HELP = """
Add your AskAnna API key to your global configuration file
(~/.askanna.yml). This is necessary to gain access to projects associated with
your AskAnna account.
"""

SHORT_HELP = "Login and save your AskAnna API key"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option('--email', '-e', required=False, type=str, help="Email which you use to login")
@click.option('--password', '-p', required=False, type=str, help="Password you use to login")
@click.option('--remote', '-r', required=False, type=str, help="Remote you want to login to")
def cli(email: str = None, password: getpass = None, remote: str = None):
    auth = AuthGateway()
    token = askanna_client.config.user.token

    if token:
        # Showcase with this token, who we are and provide info what do to if you want to use another account
        user = auth.get_user_info()
        if user.name:
            click.echo("You are already logged in as '{}' with email '{}'".format(user.name, user.email))
        else:
            click.echo("You are already logged in with email '{}'".format(user.email))

        click.echo("If you want to log in with another account, please first log out: "
                   "`askanna logout`")
        sys.exit(0)

    if email and password:
        pass
    else:
        click.echo("Let's login into AskAnna")
        if not email:
            email = click.prompt("Email", type=str)
        if not password:
            password = click.prompt("Password", type=str, hide_input=True)

    # Do the actual login and update the config file with the token
    token = auth.login(email=email, password=password, remote=remote, update_config_file=True)

    if token:
        user = auth.get_user_info()

        if user.name:
            click.echo("You are logged in as '{}' with email '{}'".format(user.name, user.email))
        else:
            click.echo("You are logged in with email '{}'".format(user.email))
