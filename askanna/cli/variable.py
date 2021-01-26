import sys
import click

from askanna import variable as aa_variable

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
@click.option('--project', '-p', 'project_suuid', required=False, type=str,
              help='Project SUUID to list variables for a project')
def list(project_suuid):
    """
    List variables
    """
    variables = aa_variable.list(project_suuid)

    if not variables:
        print("Based on the information provided, we cannot find any variables.")
        sys.exit(0)
    if project_suuid:
        print("The variables for project \"{}\" are:\n".format(variables[0].project['name']))
        print("VARIABLE SUUID         VARIABLE NAME")
        print("-------------------    -------------------------")
    else:
        print("PROJECT SUUID          PROJECT NAME       VARIABLE SUUID         VARIABLE NAME")
        print("-------------------    ---------------    -------------------    -------------------------")
    for var in sorted(variables, key=lambda x: (x.project['name'], x.name)):
        if project_suuid:
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
@click.option('--id', '-i', 'variable_suuid', required=True, type=str, help='Variable SUUID')
@click.option('--name', '-n', required=False, type=str, help='New name to set')
@click.option('--value', '-v', required=False, type=str, help='New value to set')
@click.option('--masked', '-m', required=False, type=bool, help='Set value to masked')
def change(variable_suuid, name, value, masked):
    """
    Change a variable name, value and if the value should set to be masked.
    We will only proceed when any of the name or value is set.
    """
    variable = aa_variable.detail(short_uuid=variable_suuid)

    if not any([name, value]):
        print("We did not change anything because you did not request to change a name or value.\n"
              "Please add additional input to the command to change the name or value of the variable.")
        sys.exit(0)
    if masked and variable.is_masked:
        print("This variable is currently masked. It is not possible to unmask a masked variable."
              "We skip the option to change the mask status of the variable.")
        sys.exit(0)

    # commit the change of the variable to AskAnna
    aa_variable.change(short_uuid=variable_suuid, name=name, value=value, is_masked=masked)


@cli3.command(help="Delete a variable in AskAnna", short_help="Delete variable")
@click.option('--id', '-i', 'variable_suuid', required=True, type=str, help='Job variable SUUID')
@click.option('--force', '-f', is_flag=True, help='Force')
def delete(variable_suuid, force):
    """
    Delete a variable in AskAnna
    """
    try:
        variable = aa_variable.detail(short_uuid=variable_suuid)
    except TypeError:
        print(
            "It seems that a variable {id} doesn't exist.".format(id=id)
        )
        sys.exit(1)

    def ask_confirmation() -> bool:
        confirm = input("Are you sure to delete variable {id} with name \"{name}\"? [y/n]: ".format(
            id=variable_suuid, name=variable.name
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

    deleted = aa_variable.delete(short_uuid=variable_suuid)
    if deleted:
        print("You deleted variable {id}".format(id=id))
    else:
        print("Something went wrong, deletion not performed.")


@cli4.command(help="Create a variable for a project in AskAnna", short_help="Create variable")
@click.option('--name', '-n', required=True, type=str, help='Name of the variable')
@click.option('--value', '-v', required=True, type=str, help='Value of the variable')
@click.option('--masked', '-m', required=False, type=bool, default=False,
              help='Set value to masked (default is False)')
@click.option('--project', '-p', 'project_suuid', required=True, type=str,
              help='Project SUUID where this variable will be created')
def add(name, value, masked, project_suuid):
    """
    Add a variable to a project
    """
    variable, created = aa_variable.create(name=name, value=value, is_masked=masked,
                                           project=project_suuid)
    if created:
        print("You created variable \"{name}\" with SUUID {id}.".format(
            name=variable.name, id=variable.short_uuid))
        sys.exit(0)
    else:
        print("Something went wrong in creating the variable.")
        sys.exit(1)


cli = click.CommandCollection(sources=[cli1, cli2, cli3, cli4], help=HELP,
                              short_help=SHORT_HELP)
