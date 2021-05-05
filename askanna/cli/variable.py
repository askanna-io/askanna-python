import sys
import click

from askanna import variable as aa_variable
from askanna.cli.utils import ask_which_project, ask_which_workspace
from askanna.core.config import Config
from askanna.core.utils import extract_push_target, getProjectInfo


config = Config()

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
@click.option("--project", "-p", "project_suuid", required=False, type=str,
              help="Project SUUID to list variables for a project")
def list(project_suuid):
    """
    List variables
    """
    variables = aa_variable.list(project_suuid)

    if not variables:
        click.echo("Based on the information provided, we cannot find any variables.")
        sys.exit(0)
    if project_suuid:
        click.echo("The variables for project \"{}\" are:\n".format(variables[0].project['name']))
        click.echo("VARIABLE SUUID         VARIABLE NAME")
        click.echo("-------------------    -------------------------")
    else:
        click.echo("PROJECT SUUID          PROJECT NAME            VARIABLE SUUID         VARIABLE NAME")
        click.echo("-------------------    --------------------    -------------------    -------------------------")

    for var in sorted(variables, key=lambda x: (x.project['name'], x.name)):
        if project_suuid:
            click.echo(
                "{suuid}    {variable_name}".format(
                    suuid=var.short_uuid,
                    variable_name=var.name[:25]
                )
            )
        else:
            click.echo(
                "{project_suuid}    {project_name}    {variable_suuid}    {variable_name}".format(
                    project_suuid=var.project['short_uuid'],
                    project_name="{:20}".format(var.project['name'])[:20],
                    variable_suuid=var.short_uuid,
                    variable_name=var.name[:25]
                )
            )


@cli2.command(help="Change a variable in AskAnna", short_help="Change variable")
@click.option("--id", "-i", "suuid", required=True, type=str, help="Variable SUUID")
@click.option("--name", "-n", required=False, type=str, help="New name to set")
@click.option("--value", "-v", required=False, type=str, help="New value to set")
@click.option("--masked", "-m", required=False, type=bool, help="Set value to masked")
def change(suuid, name, value, masked):
    """
    Change a variable name, value and if the value should set to be masked.
    We will only proceed when any of the name or value is set.
    """
    variable = aa_variable.detail(suuid=suuid)

    if not any([name, value]):
        click.echo("We did not change anything because you did not request to change a name or value.\n"
                   "Please add additional input to the command to change the name or value of the variable.", err=True)
        sys.exit(0)
    if masked and variable.is_masked:
        click.echo("This variable is currently masked. It is not possible to unmask a masked variable."
                   "We skip the option to change the mask status of the variable.", err=True)
        sys.exit(0)

    # commit the change of the variable to AskAnna
    aa_variable.change(suuid=suuid, name=name, value=value, is_masked=masked)


@cli3.command(help="Delete a variable in AskAnna", short_help="Delete variable")
@click.option("--id", "-i", "suuid", type=str, required=True, help="Job variable SUUID")
@click.option("--force", "-f", is_flag=True, help="Force")
def delete(suuid, force):
    """
    Delete a variable in AskAnna
    """
    try:
        variable = aa_variable.detail(suuid=suuid)
    except TypeError:
        click.echo(
            "It seems that a variable {id} doesn't exist.".format(id=id),
            err=True
        )
        sys.exit(1)

    def ask_confirmation() -> bool:
        confirm = input("Are you sure to delete variable {suuid} with name \"{name}\"? [y/n]: ".format(
            suuid=suuid, name=variable.name
        ))
        answer = confirm.strip()
        if answer not in ['n', 'y']:
            click.echo("Invalid option selected, choose from y or n")
            return ask_confirmation()
        if confirm == 'y':
            return True
        else:
            return False

    if not force:
        confirmation = ask_confirmation()
        if not confirmation:
            click.echo("Understood. We are not deleting the variable.")
            sys.exit(0)

    deleted = aa_variable.delete(suuid=suuid)
    if deleted:
        click.echo("You deleted variable {suuid}".format(suuid=suuid))
    else:
        click.echo("Something went wrong, deletion not performed.", err=True)


@cli4.command(help="Add a variable to a project in AskAnna", short_help="Add variable")
@click.option("--name", "-n", required=False, type=str, help="Name of the variable")
@click.option("--value", "-v", required=False, type=str, help="Value of the variable")
@click.option("--masked/--not-masked", "-m", "masked", default=False, show_default=False,
              help="Set value to masked (default is not-masked)")
@click.option("--project", "-p", "project_suuid", type=str, required=False,
              help="Project SUUID where this variable will be created")
def add(name, value, masked, project_suuid):
    """
    Add a variable to a project
    """

    if project_suuid:
        project = getProjectInfo(project_suuid=project_suuid)
        click.echo(f"Selected project: {project.name}")
    else:
        # Use the project from the push-target if not set
        try:
            push_target = extract_push_target(config.push_target)
        except ValueError:
            # the push-target is not set, so don't bother reading it
            pass
        else:
            project = getProjectInfo(project_suuid=project_suuid)
            if click.confirm(f"\nDo you want to create a variable for project \"{project.name}\"?"):
                project_suuid = push_target.get("project_suuid")
                click.echo(f"Selected project: {project.name}")

    if not project_suuid:
        workspace = ask_which_workspace(question="In which workspace do you want to add a variable?")
        project = ask_which_project(
            question="In which project do you want to add a variable?",
            workspace_suuid=workspace.short_uuid
        )

    confirm = False
    if not name:
        name = click.prompt("\nName of the new variable", type=str)
        confirm = True

    if not value:
        value = click.prompt("Value of the new variable", type=str)
        confirm = True

        if not masked:
            masked = click.prompt("Should the value be masked in logs and the web interface? [y/N]", type=bool)

    if confirm:
        click.confirm(f"\nDo you want to create the variable \"{name}\" in project \"{project.name}\"?", abort=True)

    variable, created = aa_variable.create(name=name, value=value, is_masked=masked, project_suuid=project.short_uuid)
    if created:
        click.echo(f"\nYou created variable \"{variable.name}\" with SUUID {variable.short_uuid} in project "
                   f"\"{project.name}\"")
        sys.exit(0)
    else:
        click.echo("Something went wrong in creating the variable.", err=True)
        sys.exit(1)


cli = click.CommandCollection(sources=[cli1, cli2, cli3, cli4], help=HELP,
                              short_help=SHORT_HELP)
