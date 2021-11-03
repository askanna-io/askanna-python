import os
import yaml

import click

from askanna.cli.utils import ask_which_workspace
from askanna.core.apiclient import client


HELP = """
This command will allow you to create an AskAnna project in your current directory
"""

SHORT_HELP = "Create a project in the current directory"


class CreateProject:
    def __init__(self, name: str = None):
        self.client = client
        self.name = name

    def cli(self, workspace_suuid: str = None, description: str = None):
        if not self.name:
            click.echo(
                "Hi! It is time to create a new project in AskAnna. "
                "We start with some information about the project.\n"
            )
            self.name = click.prompt("Project name", type=str)

            if not description:
                description = click.prompt(
                    "Project description", type=str, default="", show_default=False
                )

        if not workspace_suuid:
            workspace = ask_which_workspace("In which workspace do you want to create the new project?")
            workspace_suuid = workspace.short_uuid

        url = f"{self.client.base_url}project/"
        r = self.client.post(
            url,
            data={
                "name": self.name,
                "workspace": workspace_suuid,
                "description": description,
            },
        )
        if r.status_code == 201:
            click.echo("\nYou have successfully created a new project in AskAnna!")
            return r.json()
        else:
            raise Exception("We could not create the project.")


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
            "This directory already has an 'askanna.yml' file. If you continue, we will "
            "create a new project in AskAnna."
        )
        click.echo(
            "But, we will not update your 'askanna.yml' file with the push-target of the "
            "new project. If you continue, you need to add the push-target yourself.\n"
        )
        click.confirm(
            "Do you want to continue without updating the 'askanna.yml'?", abort=True
        )
        click.echo("")

    project_creator = CreateProject(name=name)
    project_info = project_creator.cli(workspace_suuid=workspace, description=description)

    if not os.path.exists(askanna_project_file):
        with open(askanna_project_file, "w") as pf:
            pf.write(yaml.dump({"push-target": project_info["url"]}, indent=2))
    else:
        click.echo(
            "\nTo be able to push your code to AskAnna, you need to update your local `askanna.yml` file. "
            "In the `askanna.yml` set or update the push-target with:"
        )
        click.echo("push-target: {}".format(project_info["url"]))

    # finish
    click.echo("\nCheck your project in AskAnna at:")
    click.echo("{project_url}".format(project_url=project_info["url"]))
    click.echo(
        "\nAs a first step you can configure your first job for this project in the `askanna.yml` file. "
        "Ones you are done, you can easily push your code to AskAnna via:\n"
        "\n"
        "  askanna push\n"
        "\n"
        "Success with your project!"
    )
