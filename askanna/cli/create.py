import click
from cookiecutter.main import cookiecutter as cookiecreator
from cookiecutter.exceptions import OutputDirExistsException
import os
from slugify import slugify

from askanna.cli.utils import ask_which_workspace
from askanna.core.apiclient import client
from askanna.core.push import push
from askanna.settings import DEFAULT_PROJECT_TEMPLATE


HELP = """
This command will allow you to create an AskAnna project in a new directory
"""

SHORT_HELP = "Create a project in a new directory"


class CreateProject:
    def __init__(self, name: str = None):
        self.client = client
        self.name = name
        self.slugified_name = None
        if self.name:
            self.slugified_name = slugify(self.name)

    def cli(self, workspace_suuid: str = None, description: str = None):
        if not self.name:
            click.echo(
                "Hi! It is time to create a new project in AskAnna. "
                "We start with some information about the project.\n"
            )
            self.name = click.prompt("Project name", type=str)
            self.slugified_name = slugify(self.name)

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
@click.option("--description", "-d", help="Description of the project [optional]")
@click.option(
    "--template",
    "-t",
    "project_template",
    help="Location of a Cookiecutter project template",
)
@click.option(
    "--push/--no-push",
    "-p",
    "is_push",
    default=False,
    show_default=False,
    help="Push an initial version of the code [default: no-push]",
)
def cli(name, workspace, description, project_template, is_push):
    project_creator = CreateProject(name=name)
    project_info = project_creator.cli(workspace_suuid=workspace, description=description)
    project_dir = project_creator.slugified_name
    if not project_template:
        project_template = DEFAULT_PROJECT_TEMPLATE

    try:
        cookiecreator(
            project_template,
            no_input=True,
            overwrite_if_exists=False,
            extra_context={
                "project_name": project_info["name"],
                "project_directory": project_dir,
                "project_push_target": project_info["url"],
            },
        )
    except OutputDirExistsException:
        click.echo(
            f"You already have a project directory '{project_dir}'."
            + " If you open the new project in AskAnna, you find instructions about "
            + "how you can push your project to AskAnna."
        )
    else:
        click.echo(f"Open your new local project directory: 'cd {project_dir}'")

        if is_push:
            click.echo("")  # print an empty line

            # also push the new directory to AskAnna
            os.chdir(project_dir)
            push(force=True, description="Initial push")

    # finish
    click.echo(
        "\nWe have setup the new project. You can check your project in AskAnna at:"
    )
    click.echo(project_info["url"])
    click.echo("\nSuccess with your project!")
