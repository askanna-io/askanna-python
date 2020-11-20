import sys

import click

from askanna.cli.core import client as askanna_client
from askanna.cli.utils import get_config

HELP = """
Change variables in AskAnna
"""

SHORT_HELP = "Change variables in AskAnna"


@click.group()
def cli1():
    pass


@click.group()
def cli2():
    pass


@cli1.command(help="List variables", short_help="List variables")
def list():
    """
    List variables
    """

    config = get_config()
    ASKANNA_API_SERVER = config.get('askanna', {}).get('remote')

    base_url = "{server}".format(server=ASKANNA_API_SERVER)
    url = base_url + "variable/"

    # first try to get the variable (if http=200, then access and ok)
    r = askanna_client.get(url)
    if r.status_code != 200:
        print("We cannot find variables for you")
        sys.exit(1)

    variables = r.json()
    for var in sorted(variables, key=lambda x: x['name']):
        print("{}: {}".format(var['short_uuid'], var['name']))


@cli2.command(help=HELP, short_help=SHORT_HELP)
@click.option('--id', '-i', required=True, type=str, help='Job variable SUUID')
@click.option('--value', '-v', required=True, type=str, help='New value to set')
def change(id, value):
    config = get_config()
    ASKANNA_API_SERVER = config.get('askanna', {}).get('remote')

    base_url = "{server}".format(server=ASKANNA_API_SERVER)
    url = base_url + "variable/{}/".format(id)
    click.echo("Let's change variable {}".format(id))

    # first try to get the variable (if http=200, then access and ok)
    r = askanna_client.get(url)
    if r.status_code != 200:
        print("We cannot find the variable you tried to change, or you don't have access to change this variable.")
        print("No change performed")
        sys.exit(1)

    # emit update request (PATCH)

    r = askanna_client.patch(
        url,
        data={
            "value": value
        }
    )

    # show success or failure
    if r.status_code == 200:
        variable_name = r.json().get('name')
        print("You have successfully changed the variable: '{variable_name}'".format(variable_name=variable_name))
        sys.exit(0)
    else:
        print("Something went wrong while changing the variable")
        sys.exit(1)


cli = click.CommandCollection(sources=[cli1, cli2], help="List and modify variables",
                              short_help="List and modify variables")
