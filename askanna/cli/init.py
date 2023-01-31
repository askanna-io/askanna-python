import os
import sys

import click
import yaml

from askanna.cli.utils import ask_which_workspace
from askanna.config import config
from askanna.core.dataclasses.project import Project
from askanna.sdk.project import ProjectSDK

HELP = """
This command will allow you to create an AskAnna project in your current directory
"""

SHORT_HELP = "Create a project in the current directory"


class CreateProject:
    def __init__(self, name: str = ""):
        self.name = name

    def cli(self, workspace_suuid: str = "", description: str = "") -> Project:
        if not self.name:
            click.echo(
                "Hi! It is time to create a new project in AskAnna. "
                "We start with some information about the project.\n"
            )
            self.name = click.prompt("Project name", type=str)

            if not description:
                description = click.prompt("Project description", type=str, default="", show_default=False)

        if not workspace_suuid:
            workspace = ask_which_workspace("In which workspace do you want to create the new project?")
            workspace_suuid = workspace.suuid

        try:
            project = ProjectSDK().create(workspace_suuid=workspace_suuid, name=self.name, description=description)
        except Exception as e:
            click.echo(f"Something went wrong while creating the project:\n  {e}", err=True)
            sys.exit(1)
        else:
            click.echo(f"\nYou successfully created project '{project.name}' with SUUID '{project.suuid}'")
            return project


@click.command(help=HELP, short_help=SHORT_HELP)
@click.argument("name", required=False)
@click.option(
    "--workspace",
    "-w",
    show_default=True,
    help="Workspace SUUID where you want to create the project",
)
@click.option("--description", "-d", help="Description of the project")
def cli(name, workspace, description):
    cwd = os.getcwd()
    askanna_project_file = os.path.join(cwd, "askanna.yml")
    if os.path.exists(askanna_project_file):
        click.echo(
            "This directory already has an 'askanna.yml' file. If you continue, we will create a new project in "
            "AskAnna."
        )
        click.echo(
            "We will not update your 'askanna.yml' file with the push-target of the new project. If you continue, you "
            "need to add the push-target yourself.\n"
        )
        click.confirm("Do you want to continue without updating the 'askanna.yml'?", abort=True)
        click.echo("")

    project_creator = CreateProject(name=name)
    project_info = project_creator.cli(workspace_suuid=workspace, description=description)

    if config.server.ui:
        project_url = config.server.ui + "/" + project_info.workspace.suuid + "/project/" + project_info.suuid + "/"
    else:
        project_url = config.server.remote + "/v1/project/" + project_info.suuid + "/"

    if not os.path.exists(askanna_project_file):
        with open(askanna_project_file, "w") as pf:
            pf.write(yaml.dump({"push-target": project_url}, indent=2))
    else:
        click.echo(
            "\nTo be able to push your code to AskAnna, you need to update your local `askanna.yml` file. "
            "In the `askanna.yml` set or update the push-target with:"
        )
        click.echo(f"push-target: {project_url}")

    if config.server.ui:
        click.echo("\nWe have setup the new project. You can open your project at:")
        click.echo(project_url)
    else:
        click.echo("\nWe have setup the new project.")
    click.echo(
        "\nAs a first step you can configure your first job for this project in the `askanna.yml` file."
        "\nOnes you are done, you can push your code to AskAnna with the command:\n"
        "\n"
        "  askanna push\n"
        "\n"
        "More info about creating jobs: https://docs.askanna.io/job/create-job/\n"
        "\n"
        "Success with your project!"
    )
