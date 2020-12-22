import getpass
import sys

import click

from askanna.cli.core import client as askanna_client
from askanna.cli.utils import get_config, store_config, CONFIG_FILE_ASKANNA

HELP = """
Add your AskAnna API key to your global configuration file
(~/.askanna.yml). This is necessary to gain access to projects associated with
your AskAnna account.
"""

SHORT_HELP = "Login and save your AskAnna API key"


def login(server):
    url = "{server}rest-auth/login/".format(server=server.replace("v1/", ''))
    print("Please provide your credentials to log into AskAnna")
    email = input("Email: ")
    password = getpass.getpass()
    login_dict = {
        'username': email.strip(),
        'password': password.strip()
    }

    r = askanna_client.post(url, json=login_dict)
    if r.status_code == 200:
        token = r.json().get('key')
        return str(token)
    elif r.status_code == 400:
        print("We could not log you in. Please check your credentials.")
        sys.exit(1)
    sys.exit(1)


def get_user_info(token, server):

    url = "{server}rest-auth/user".format(server=server.replace("v1/", ''))
    ruser = askanna_client.get(url)
    if ruser.status_code == 200:
        result = ruser.json()
        print("You are logged in as {} with email {}".format(result['name'], result['email']))
    elif ruser.status_code == 401:
        print("The provided token is not valid. Via `askanna logout` you can remove the token "
              "and via `askanna login` you can set a new token.")
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
    with open(CONFIG_FILE_ASKANNA, "w") as fd:
        fd.write(config)

    return token


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    config = get_config(check_config=False)

    ASKANNA_API_SERVER = config.get('askanna', {}).get('remote')

    click.echo("Login into AskAnna")

    if config.get('auth'):
        if config['auth'].get('token'):
            # validate_token()
            token = config['auth']['token']
            # Showcase with this token, who we are
            get_user_info(token, server=ASKANNA_API_SERVER)
            click.echo("If you want to log in with another account, please first log out: "
                       "`askanna logout`")
            sys.exit(0)

    token = do_login(server=ASKANNA_API_SERVER)
    if token:
        get_user_info(token, server=ASKANNA_API_SERVER)
