import sys

import click

from askanna.config import config
from askanna.core.auth import AuthGateway

HELP = """
Add your AskAnna API key to your global configuration file
(~/.askanna.yml). This is necessary to gain access to projects associated with
your AskAnna account.
"""

SHORT_HELP = "Login and save your AskAnna API token"


@click.command(help=HELP, short_help=SHORT_HELP)
@click.option("--email", "-e", required=False, type=str, help="Email which you use to login")
@click.option("--password", "-p", required=False, help="Password you use to login")
@click.option("--url", required=False, type=str, help="URL you want to login to")
@click.option("--remote", "-r", required=False, type=str, help="Remote you want to login to")
def cli(email: str, password: str, url: str, remote: str):
    auth = AuthGateway()

    if config.server.is_authenticated:
        # Showcase with this token, who we are and provide info what do to if you want to use another account
        user = auth.get_user_info()
        click.echo("You are already logged in with email '{}'".format(user.email))
        click.echo("If you want to log in with another account, please first log out: `askanna logout`")
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
    auth.login(email=email, password=password, remote_url=remote, ui_url=url, update_config_file=True)
    user = auth.get_user_info()
    click.echo("You are logged in with email '{}'.".format(user.email))
