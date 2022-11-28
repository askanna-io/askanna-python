import os
import sys

import click
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter as cookiecreator
from slugify import slugify

from askanna import project as aa_project
from askanna.cli.utils import ask_which_workspace
from askanna.config import config
from askanna.core.dataclasses.project import Project
from askanna.core.push import push
from askanna.settings import DEFAULT_PROJECT_TEMPLATE

HELP = """
This command will allow you to create an AskAnna project in a new directory
"""

SHORT_HELP = "Create a project in a new directory"


class CreateProject:
    def __init__(self, name: str = ""):
        self.name = name
        if self.name:
            self.slugified_name = slugify(self.name)

    def cli(self, workspace_suuid: str = "", description: str = "") -> Project:
        if not self.name:
            click.echo(
                "Hi! It is time to create a new project in AskAnna. "
                "We start with some information about the project.\n"
            )
            self.name = click.prompt("Project name", type=str)
            self.slugified_name = slugify(self.name)

            if not description:
                description = click.prompt("Project description", type=str, default="", show_default=False)

        if not workspace_suuid:
            workspace = ask_which_workspace("In which workspace do you want to create the new project?")
            workspace_suuid = workspace.suuid

        try:
            project = aa_project.create(workspace_suuid=workspace_suuid, name=self.name, description=description)
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
    cwd = os.getcwd()
    askanna_project_file = os.path.join(cwd, "askanna.yml")
    if os.path.exists(askanna_project_file):
        click.echo(
            "This directory already has an 'askanna.yml' file and we cannot create a new project directory within an "
            "AskAnna project directory.",
            err=True,
        )
        sys.exit(1)

    project_creator = CreateProject(name=name)
    project_info = project_creator.cli(workspace_suuid=workspace, description=description)
    project_dir = project_creator.slugified_name

    try:
        cookiecreator(
            project_template or DEFAULT_PROJECT_TEMPLATE,
            no_input=True,
            overwrite_if_exists=False,
            extra_context={
                "project_name": project_info.name,
                "project_directory": project_dir,
                "project_push_target": project_info.url,
            },
        )
    except OutputDirExistsException:
        click.echo(
            f"You already have a project directory '{project_dir}'. If you open the new project in AskAnna, you find "
            "instructions about how you can push your project to AskAnna. You can open your project at:"
        )
        click.echo(project_info.url)
        click.echo("\nSuccess with your project!")
        sys.exit(1)
    else:
        click.echo(f"Open your new local project directory: 'cd {project_dir}'")

        if is_push:
            # Also push the new directory to AskAnna
            click.echo("")
            config.project.reload_config(os.path.join(os.getcwd(), project_dir, "askanna.yml"))
            push(description="Initial push")

    click.echo("\nWe have setup the new project. You can open your project at:")
    click.echo(project_info.url)
    click.echo("\nSuccess with your project!")
