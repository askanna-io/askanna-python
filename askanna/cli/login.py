import sys

import click

from askanna.config import config
from askanna.gateways.auth import AuthGateway

HELP = """
Add your AskAnna API key to your global configuration file (~/.askanna.yml). This is necessary to gain access to
projects associated with your AskAnna account.
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
        click.echo(f"You are already logged in with email '{user.email}'.")

        logout = click.confirm(f"Do you want to log out email '{user.email}' and log in with another account?")
        if logout:
            config.server.logout_and_remove_token()
        else:
            click.echo("Login with a new account aborted.")
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
    try:
        auth.login(email=email, password=password, remote_url=remote, ui_url=url, update_config_file=True)
    except Exception as e:
        click.echo(f"Login to AskAnna failed:\n  {e}")
        sys.exit(1)

    user = auth.get_user_info()
    click.echo(f"You are logged in with email '{user.email}'")
