import sys

import click

from askanna.cli.core.variables import VariableGateway

HELP = """
Manage your variables in AskAnna
"""

SHORT_HELP = "Manage variables in AskAnna"


@click.group()
def cli1():
    pass


@click.group()
def cli2():
    pass


@click.group()
def cli3():
    pass


@click.group()
def cli4():
    pass


@cli1.command(help="List variables in AskAnna", short_help="List variables")
@click.option('--project', '-p', required=False, type=str, help='Project SUUID to list variables for a project')
def list(project):
    """
    List variables
    """
    variable_gateway = VariableGateway()
    variables = variable_gateway.list(project=project)
    if not variables:
        print("Based on the information provided, we cannot find any variables.")
        sys.exit(0)
    if project:
        print("The variables for project \"{}\" are:\n".format(variables[0].project['name']))
        print("VARIABLE SUUID         VARIABLE NAME")
        print("-------------------    -------------------------")
    else:
        print("PROJECT SUUID          PROJECT NAME       VARIABLE SUUID         VARIABLE NAME")
        print("-------------------    ---------------    -------------------    -------------------------")
    for var in sorted(variables, key=lambda x: (x.project['name'], x.name)):
        if project:
            print("{suuid}    {variable_name}".format(
                suuid=var.short_uuid,
                variable_name=var.name))
        else:
            print("{project_suuid}    {project}    {suuid}    {variable_name}".format(
                project_suuid=var.project['short_uuid'],
                project="{:15}".format(var.project['name']),
                suuid=var.short_uuid,
                variable_name=var.name))


@cli2.command(help="Change a variable in AskAnna", short_help="Change variable")
@click.option('--id', '-i', required=True, type=str, help='Variable SUUID')
@click.option('--name', '-n', required=False, type=str, help='New name to set')
@click.option('--value', '-v', required=False, type=str, help='New value to set')
@click.option('--masked', '-m', required=False, type=bool, help='Set value to masked')
def change(id, name, value, masked):
    """
    Change a variable name, value and if the value should set to be masked.
    We will only proceed when any of the name or value is set.
    """
    short_uuid = id

    variable_gateway = VariableGateway()
    variable = variable_gateway.detail(short_uuid)

    if not any([name, value]):
        print("We did not change anything because you did not request to change a name or value.\n"
              "Please add additional input to the command to change the name or value of the variable.")
        sys.exit(0)
    if masked and variable.is_masked:
        print("This variable is currently masked. It is not possible to unmask a masked variable."
              "We skip the option to change the mask status of the variable.")
    # change the details of the variable
    variable.name = name or variable.name
    variable.value = value or variable.value
    variable.is_masked = masked or variable.is_masked

    # commit the change of the variable to AskAnna
    variable = variable_gateway.change(short_uuid, variable)


@cli3.command(help="Delete a variable in AskAnna", short_help="Delete variable")
@click.option('--id', '-i', required=True, type=str, help='Job variable SUUID')
@click.option('--force', '-f', is_flag=True, help='Force')
def delete(id, force):
    """
    Delete a variable in AskAnna
    """
    short_uuid = id
    variable_gateway = VariableGateway()
    try:
        variable = variable_gateway.detail(short_uuid)
    except TypeError:
        print(
            "It seems that a variable {id} doesn't exist.".format(id=id)
        )
        sys.exit(1)

    def ask_confirmation() -> bool:
        confirm = input("Are you sure to delete variable {id} with name \"{name}\"? [y/n]: ".format(
            id=id, name=variable.name
        ))
        answer = confirm.strip()
        if answer not in ['n', 'y']:
            print("Invalid option selected, choose from y or n")
            return ask_confirmation()
        if confirm == 'y':
            return True
        else:
            return False

    if not force:
        confirmation = ask_confirmation()
        if not confirmation:
            print("Understood. We are not deleting the variable.")
            sys.exit(0)

    variable_gateway = VariableGateway()
    deleted = variable_gateway.delete(short_uuid)
    if deleted:
        print("You deleted variable {id}".format(id=id))
    else:
        print("Something went wrong, deletion not performed.")


@cli4.command(help="Create a variable for a project in AskAnna", short_help="Create variable")
@click.option('--name', '-n', required=True, type=str, help='Name of the variable')
@click.option('--value', '-v', required=True, type=str, help='Value of the variable')
@click.option('--masked', '-m', required=False, type=bool, default=False, help='Set value to masked (default is False)')
@click.option('--project', '-p', required=True, type=str, help='Project SUUID where this variable will be created')
def add(name, value, masked, project):
    """
    Add a variable to a project
    """
    variable_gateway = VariableGateway()
    # Add variable to askanna
    variable, created = variable_gateway.create(name, value, masked, project)
    if created:
        print("You created variable \"{name}\" with SUUID {id}.".format(
            name=variable.name, id=variable.short_uuid))
        sys.exit(0)
    else:
        print("Something went wrong in creating the variable.")
        sys.exit(1)


cli = click.CommandCollection(sources=[cli1, cli2, cli3, cli4], help=HELP,
                              short_help=SHORT_HELP)
