import sys

import click

from askanna import project as aa_project
from askanna import variable as aa_variable
from askanna.cli.utils import ask_which_project, ask_which_workspace
from askanna.config import config
from askanna.core.dataclasses.project import Project


@click.group()
def cli1():
    pass


@cli1.command(help="List variables in AskAnna", short_help="List variables")
@click.option(
    "--project", "-p", "project_suuid", required=False, type=str, help="Project SUUID to list variables for a project"
)
def list(project_suuid):
    """
    List variables
    """
    variables = aa_variable.list(project_suuid=project_suuid)

    if not variables:
        click.echo("Based on the information provided, we cannot find any variables.")
        sys.exit(0)
    if project_suuid:
        click.echo(f'The variables for project "{variables[0].project.name}" are:\n')
        click.echo("VARIABLE SUUID         VARIABLE NAME")
        click.echo("-------------------    -------------------------")
    else:
        click.echo("PROJECT SUUID          PROJECT NAME            VARIABLE SUUID         VARIABLE NAME")
        click.echo("-------------------    --------------------    -------------------    -------------------------")

    for var in sorted(variables, key=lambda x: (x.project.name, x.name)):
        if project_suuid:
            click.echo(f"{var.suuid}    {var.name[:25]}")
        else:
            click.echo(
                "{project_suuid}    {project_name}    {variable_suuid}    {variable_name}".format(
                    project_suuid=var.project.suuid,
                    project_name=f"{var.project.name:20}"[:20],
                    variable_suuid=var.suuid,
                    variable_name=var.name[:25],
                )
            )


@cli1.command(help="Change a variable in AskAnna", short_help="Change variable")
@click.option("--id", "-i", "suuid", required=True, type=str, help="Variable SUUID")
@click.option("--name", "-n", required=False, type=str, help="New name to set")
@click.option("--value", "-v", required=False, type=str, help="New value to set")
@click.option("--masked", "-m", required=False, type=bool, help="Set value to masked")
def change(suuid, name, value, masked):
    """
    Change a variable name, value and if the value should set to be masked.
    We will only proceed when any of the name or value is set.
    """
    variable = aa_variable.detail(variable_suuid=suuid)

    if not any([name, value]):
        click.echo(
            "We did not change anything because you did not request to change a name or value.\n"
            "Please add additional input to the command to change the name or value of the variable.",
            err=True,
        )
        sys.exit(0)
    if masked and variable.is_masked:
        click.echo(
            "This variable is currently masked. It is not possible to unmask a masked variable."
            "We skip the option to change the mask status of the variable.",
            err=True,
        )
        sys.exit(0)

    # commit the change of the variable to AskAnna
    aa_variable.change(variable_suuid=suuid, name=name, value=value, is_masked=masked)


@cli1.command(help="Remove a variable in AskAnna", short_help="Remove variable")
@click.option("--id", "-i", "suuid", type=str, required=True, help="Variable SUUID", prompt="Variable SUUID")
@click.option("--force", "-f", is_flag=True, help="Force")
def remove(suuid, force):
    """
    Delete a variable in AskAnna
    """
    try:
        variable = aa_variable.detail(variable_suuid=suuid)
    except TypeError:
        click.echo(f"It seems that a variable {suuid} doesn't exist.", err=True)
        sys.exit(1)

    if not force:
        if not click.confirm(f'Are you sure to delete variable {suuid} with name "{variable.name}"?'):
            click.echo("Understood. We are not deleting the variable.")
            sys.exit(0)

    deleted = aa_variable.delete(variable_suuid=suuid)
    if deleted:
        click.echo(f"You deleted variable {suuid}")
    else:
        click.echo("Something went wrong, deletion not performed.", err=True)


@cli1.command(help="Add a variable to a project in AskAnna", short_help="Add variable")
@click.option("--name", "-n", required=False, type=str, help="Name of the variable")
@click.option("--value", "-v", required=False, type=str, help="Value of the variable")
@click.option(
    "--masked/--not-masked",
    "-m",
    "masked",
    default=False,
    show_default=False,
    help="Set value to masked (default is not-masked)",
)
@click.option(
    "--project",
    "-p",
    "project_suuid",
    type=str,
    required=False,
    help="Project SUUID where this variable will be created",
)
def add(name, value, masked, project_suuid):
    """
    Add a variable to a project
    """

    project = None
    if project_suuid:
        project = aa_project.get(project_suuid=project_suuid)
        click.echo(f"Selected project: {project.name}")
    elif config.project.project_suuid:
        project = aa_project.get(project_suuid=config.project.project_suuid)
        if click.confirm(f'\nDo you want to create a variable for project "{project.name}"?'):
            project_suuid = project.suuid
            click.echo(f"Selected project: {project.name}")

    if not project_suuid:
        workspace = ask_which_workspace(question="In which workspace do you want to add a variable?")
        project = ask_which_project(
            question="In which project do you want to add a variable?", workspace_suuid=workspace.suuid
        )

    if type(project) is not Project:
        click.echo(
            "Something went wrong while retrieving the project information. Retrieved project is not of type Project.",
            err=True,
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
        click.confirm(f'\nDo you want to create the variable "{name}" in project "{project.name}"?', abort=True)

    try:
        variable = aa_variable.create(
            project_suuid=project.suuid,
            name=name,
            value=value,
            is_masked=masked,
        )
    except Exception as e:

        click.echo(f"Something went wrong in creating the variable:\n  {e}", err=True)
        sys.exit(1)
    else:
        click.echo(
            f'\nYou created variable "{variable.name}" with SUUID {variable.suuid} in project ' f'"{project.name}"'
        )
        sys.exit(0)


cli = click.CommandCollection(
    sources=[cli1],
    help="Manage your variables in AskAnna",
    short_help="Manage variables in AskAnna",
)
