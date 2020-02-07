import sys
import os

import click
import requests

from askanna_cli.exceptions import AlreadyLoggedInException
from askanna_cli.utils import init_checks

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

HELP = """
Add your AskAnna API key to your global configuration file
(~/.askanna.yml). This is necessary to gain access to projects associated with
your AskAnna account.

You can find your API key in AskAnna WebUI:
    https://askanna.io  #FIXME
"""

SHORT_HELP = "Save your AskAnna API key"

def login():
    url = "https://api.askanna.eu/rest-auth/login/"
    username = input("Username: ")
    password = input("Password: ")
    login_dict = {
        'username': username.strip(),
        'password': password.strip()
    }

    r = requests.post(url, json=login_dict)
    token = r.json().get('key')
    return str(token)

def get_user_info(token):

    url = "https://api.askanna.eu/rest-auth/user"

    headers = {
        'user-agent': 'askanna-cli/0.0.1',
        'Authorization': "Token {token}".format(token=token)
    }
    ruser  = requests.get(url, headers=headers)
    print(ruser.text)

def store_config(config):
    original_config = load(open(os.path.expanduser("~/.askanna.yml"), 'r'), Loader=Loader)
    original_config.update(**config)
    output = dump(original_config, Dumper=Dumper) 
    print(output)
    return output

def do_login():
    token = login()
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
    init_checks()
    config = load(open(os.path.expanduser("~/.askanna.yml"), 'r'), Loader=Loader)

    click.echo("This is performing the login action")


    if config.get('auth'):
        if config['auth'].get('token'):
            click.echo("You are already logged in")
            # validate_token()
            token = config['auth']['token']
            # Showcase with this token, who we are
            get_user_info(token)
            sys.exit()
        else:
            # click.echo("Logging in for you")
            do_login()
    else:
        do_login()
