import getpass
import sys
import os

import click
import requests

from askanna_cli.utils import get_config, store_config

HELP = """
Add your AskAnna API key to your global configuration file
(~/.askanna.yml). This is necessary to gain access to projects associated with
your AskAnna account.

You can find your API key in AskAnna WebUI:
    https://askanna.io  #FIXME
"""

SHORT_HELP = "Save your AskAnna API key"


def login(server):
    url = "{server}rest-auth/login/".format(server=server.replace("v1/", ''))
    print("Please provide your credentials to log into AskAnna")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    login_dict = {
        'username': username.strip(),
        'password': password.strip()
    }

    r = requests.post(url, json=login_dict)
    token = r.json().get('key')
    return str(token)


def get_user_info(token, server):

    url = "{server}rest-auth/user".format(server=server.replace("v1/", ''))

    headers = {
        'user-agent': 'askanna-cli/0.3.1',
        'Authorization': "Token {token}".format(token=token)
    }
    ruser = requests.get(url, headers=headers)
    if ruser.status_code == 200:
        res = ruser.json()
        print("{} {}".format(res['first_name'], res['last_name']))
    else:
        print("Could not connect to AskAnna at this moment")


def do_login(server):
    """
    Pipeline of actions to do login and store the config into local config
    """
    token = login(server=server)
    new_config = {
        'auth': {
            'token': token
        }
    }
    config = store_config(new_config)
    with open(os.path.expanduser("~/.askanna.yml"), "w") as fd:
        fd.write(config)


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    config = get_config()

    ASKANNA_API_SERVER = config.get('askanna', {}).get('remote')

    click.echo("Login into AskAnna")

    if config.get('auth'):
        if config['auth'].get('token'):
            click.echo("You are already logged in")
            # validate_token()
            token = config['auth']['token']
            # Showcase with this token, who we are
            get_user_info(token, server=ASKANNA_API_SERVER)
            sys.exit(0)
        else:
            # click.echo("Logging in for you")
            do_login(server=ASKANNA_API_SERVER)
    else:
        do_login(server=ASKANNA_API_SERVER)
