import sys

import click

from askanna.cli.utils import ask_which_project, ask_which_variable, ask_which_workspace
from askanna.config import config
from askanna.config.utils import string_format_datetime
from askanna.core.dataclasses.project import Project
from askanna.sdk.project import ProjectSDK
from askanna.sdk.variable import VariableSDK


@click.group()
def cli1():
    pass


@cli1.command(help="List variables in AskAnna", short_help="List variables")
@click.option(
    "--project", "-p", "project_suuid", required=False, type=str, help="Project SUUID to list variables for a project"
)
@click.option(
    "--workspace",
    "-w",
    "workspace_suuid",
    required=False,
    type=str,
    help="Workspace SUUID to list variables related to a workspace",
)
@click.option("--search", "-s", required=False, type=str, help="Search for a specific variable")
def list(project_suuid, workspace_suuid, search):
    variable_sdk = VariableSDK()
    try:
        variables = variable_sdk.list(
            project_suuid=project_suuid,
            workspace_suuid=workspace_suuid,
            search=search,
            order_by="project.name,name",
        )
    except Exception as e:
        click.echo(f"Something went wrong while listing the variables:\n  {e}", err=True)
        sys.exit(1)

    if not variables:
        click.echo("We cannot find any variables.")
        sys.exit(0)

    if project_suuid:
        click.echo(f"The variables for project '{variables[0].project.name}' are:")
        click.echo("")
        click.echo("-------------------    -------------------------")
        click.echo("VARIABLE SUUID         VARIABLE NAME")
        click.echo("-------------------    -------------------------")
    if not project_suuid and workspace_suuid:
        click.echo(f"The variables for workspace '{variables[0].workspace.name}' are:")
    else:
        click.echo("")
        click.echo("-------------------    --------------------    -------------------    -------------------------")
        click.echo("PROJECT SUUID          PROJECT NAME            VARIABLE SUUID         VARIABLE NAME")
        click.echo("-------------------    --------------------    -------------------    -------------------------")

    for variable in variables:
        variable_name = f"{variable.name[:22]}..." if len(variable.name) > 25 else variable.name[:25]
        if project_suuid:
            click.echo(f"{variable.suuid}    {variable_name}")
        else:
            project_name = (
                f"{variable.project.name[:17]}..." if len(variable.project.name) > 20 else variable.project.name[:20]
            )
            click.echo(
                "{project_suuid}    {project_name}    {variable_suuid}    {variable_name}".format(
                    project_suuid=variable.project.suuid,
                    project_name=f"{project_name:20}",
                    variable_suuid=variable.suuid,
                    variable_name=variable_name,
                )
            )

    if len(variables) != variable_sdk.list_total_count:
        click.echo("")
        click.echo(f"Note: the first {len(variables):,} of {variable_sdk.list_total_count:,} variables are shown.")

    click.echo("")


@cli1.command(help="Get information about a variable", short_help="Get variable info")
@click.option("--id", "-i", "variable_suuid", required=False, type=str, help="Variable SUUID")
def info(variable_suuid):
    if variable_suuid:
        try:
            variable = VariableSDK().get(variable_suuid=variable_suuid)
        except Exception as e:
            click.echo(f"Something went wrong while getting the variable info:\n  {e}", err=True)
            sys.exit(1)
    else:
        project_suuid = config.project.project_suuid
        if not project_suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to get a variable?")
            project = ask_which_project(
                question="From which project do you want to get a variable?", workspace_suuid=workspace.suuid
            )
            project_suuid = project.suuid

        variable = ask_which_variable(question="Which variable do you want to get?", project_suuid=project_suuid)

    print_list = [
        None,
        ("SUUID", variable.suuid),
        ("Name", variable.name),
        ("Value", variable.value),
        ("Masked", variable.is_masked),
        None,
        ("Project", variable.project.name),
        ("Project SUUID", variable.project.suuid),
        ("Workspace", variable.workspace.name),
        ("Workspace SUUID", variable.workspace.suuid),
        None,
        ("Created", variable.created.strftime(string_format_datetime)),
        ("Modified", variable.modified.strftime(string_format_datetime)),
        None,
    ]
    for item in print_list:
        if item is None:
            click.echo("")
        else:
            click.echo(f"{item[0] + ':':16} {item[1]}")


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
        project = ProjectSDK().get(project_suuid=project_suuid)
        click.echo(f"Selected project: {project.name}")
    elif config.project.project_suuid:
        project = ProjectSDK().get(project_suuid=config.project.project_suuid)
        if click.confirm(f'\nDo you want to create a variable for project "{project.name}"?'):
            project_suuid = project.suuid
            click.echo(f"Selected project: {project.name}")

    if not project_suuid:
        workspace = ask_which_workspace(question="In which workspace do you want to add a variable?")
        project = ask_which_project(
            question="In which project do you want to add a variable?", workspace_suuid=workspace.suuid
        )

    if not project:
        click.echo(
            "Something went wrong while retrieving the project information. Retrieved project is None.", err=True
        )
        sys.exit(1)

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
        variable = VariableSDK().add(
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
            f"\nYou succesfully created variable '{variable.name}' with SUUID '{variable.suuid}' in project "
            f"'{project.name}'"
        )
        sys.exit(0)


@cli1.command(help="Change a variable in AskAnna", short_help="Change variable")
@click.option("--id", "-i", "variable_suuid", required=False, type=str, help="Variable SUUID")
@click.option("--name", "-n", required=False, type=str, help="New name to set")
@click.option("--value", "-v", required=False, type=str, help="New value to set")
@click.option("--masked", "-m", required=False, type=bool, help="Set value to masked")
def change(variable_suuid, name, value, masked):
    """
    Change a variable name, value and if the value should set to be masked.
    We will only proceed when any of the name or value is set.
    """
    if variable_suuid:
        try:
            variable = VariableSDK().get(variable_suuid=variable_suuid)
        except Exception as e:
            click.echo(f"Something went wrong while getting the variable info:\n  {e}", err=True)
            sys.exit(1)
    else:
        project_suuid = config.project.project_suuid
        if not project_suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to change a variable?")
            project = ask_which_project(
                question="From which project do you want to change a variable?", workspace_suuid=workspace.suuid
            )
            project_suuid = project.suuid

        variable = ask_which_variable(question="Which variable do you want to change?", project_suuid=project_suuid)

    if not any([name, value, masked]):
        if click.confirm("\nDo you want to change the name of the variable?"):
            name = click.prompt("New name of the variable", type=str)
        if click.confirm("\nDo you want to change the value of the run?"):
            value = click.prompt("New value of the variable", type=str)

        if not any([name, value]):
            click.echo("We did not change anything because you did not request to change a name or value.", err=True)
            sys.exit(0)

        click.confirm("\nDo you want to change the variable?", abort=True)

    if masked and variable.is_masked:
        click.echo(
            "This variable is currently masked. It is not possible to unmask a masked variable."
            "We skip the option to change the mask status of the variable.",
            err=True,
        )
        sys.exit(0)

    try:
        variable = VariableSDK().change(variable_suuid=variable.suuid, name=name, value=value, is_masked=masked)
    except Exception as e:
        if str(e).startswith("404"):
            click.echo(f"The variable SUUID '{variable_suuid}' was not found.", err=True)
        else:
            click.echo(f"Something went wrong while changing the variable SUUID '{variable_suuid}':\n  {e}", err=True)
        sys.exit(1)

    click.echo(f"\nYou succesfully changed variable '{variable.name}' with SUUID '{variable.suuid}'")


@cli1.command(help="Remove a variable in AskAnna", short_help="Remove variable")
@click.option("--id", "-i", "variable_suuid", type=str, required=False, help="Variable SUUID", prompt="Variable SUUID")
@click.option("--force", "-f", is_flag=True, help="Force")
def remove(variable_suuid, force):
    if variable_suuid:
        try:
            variable = VariableSDK().get(variable_suuid=variable_suuid)
        except Exception as e:
            if str(e).startswith("404"):
                click.echo(f"The variable SUUID '{variable_suuid}' was not found.", err=True)
            else:
                click.echo(
                    f"Something went wrong while getting the info of variable SUUID '{variable_suuid}':\n  {e}",
                    err=True,
                )
            sys.exit(1)
    else:
        project_suuid = config.project.project_suuid
        if not project_suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to remove a variable?")
            project = ask_which_project(
                question="From which project do you want to remove a variable?", workspace_suuid=workspace.suuid
            )
            project_suuid = project.suuid

        variable = ask_which_variable(question="Which variable do you want to remove?", project_suuid=project_suuid)

    if not force:
        if not click.confirm(f'Are you sure to delete variable {variable.suuid} with name "{variable.name}"?'):
            click.echo("Understood. We are not removing the variable.")
            sys.exit(0)

    try:
        removed = VariableSDK().delete(variable_suuid=variable.suuid)
    except Exception as e:
        click.echo(f"Something went wrong while removing the variable SUUID '{variable_suuid}':\n  {e}", err=True)
        sys.exit(1)

    if removed:
        click.echo(f"You removed variable SUUID '{variable.suuid}'")
    else:
        click.echo(f"Something went wrong. Removing the run SUUID '{variable.suuid}' failed.", err=True)
        sys.exit(1)


cli = click.CommandCollection(
    sources=[cli1],
    help="Manage your variables in AskAnna",
    short_help="Manage variables in AskAnna",
)
