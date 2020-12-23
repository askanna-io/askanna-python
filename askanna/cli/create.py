import click
from cookiecutter.main import cookiecutter as cookiecreator
from cookiecutter.exceptions import OutputDirExistsException
import os
import sys
from slugify import slugify

from askanna.cli.core import client as askanna_client
from askanna.cli.utils import get_config
from askanna.cli.push import push

HELP = """
This command will allow you to create an AskAnna project
"""

SHORT_HELP = "Create an AskAnna project"
DEFAULT_DSS_PROJECT = "https://gitlab.askanna.io/open/project-templates/blanco-template.git"


def get_user_info(server):

    url = "{server}rest-auth/user".format(server=server.replace("v1/", ''))
    ruser = askanna_client.get(url)
    if ruser.status_code == 200:
        return ruser.json()
    elif ruser.status_code == 401:
        print("The provided token is not valid. Via `askanna logout` you can remove the token "
              "and via `askanna login` you can set a new token.")
    else:
        print("Could not connect to AskAnna at this moment")


class CreateProject:
    def __init__(self, name=None, api_server=None, user=None):
        self.api_server = api_server
        self.name = name
        self.user = user
        self.slugified_name = None
        if self.name:
            self.slugified_name = slugify(self.name)

    def find_workspace(self) -> list:
        """
            Find all workspaces where the user is part of and enumerate them
        """
        workspaces = []
        r = askanna_client.get('{}workspace/'.format(self.api_server))

        for workspace in r.json():
            workspaces.append({
                'suuid': workspace['short_uuid'],
                'title': workspace['title']
            })
        return workspaces

    def ask_workspace(self) -> str:
        """
        Ask which workspace the project will be created in.
        """
        workspaces = self.find_workspace()
        if len(workspaces) > 1:

            workspace_list_str = ""

            for idx, workspace in enumerate(workspaces, start=1):
                workspace_list_str += "%d. %s\n" % (idx, workspace['title'])

            workspace = click.prompt(
                "{name}, you are a member of multiple workspaces. ".format(
                    name=self.user.get("name")
                ) +
                "In which workspace do you want to create the new project?\n" +
                workspace_list_str +
                "\n" +
                "Please enter the workspace number"
            )
            selected_workspace = workspaces[int(workspace)-1]
        else:
            selected_workspace = workspaces[0]

        confirm_create = click.prompt(
            "Do you want to create a project '{project}' in '{workspace}'? (y/n)".format(
                project=self.name,
                workspace=selected_workspace['title']
            ),
            type=str
        )
        if confirm_create == 'y':
            print("Thank you for the information. Anna will continue creating the project.")
        else:
            sys.exit()

        return selected_workspace['suuid']

    def cli(self, workspace: str = None):
        if not self.name:
            self.name = click.prompt(
                "Hi {name}! It is time to create a new project in AskAnna. ".format(
                    name=self.user.get("name")
                ) +
                "We start with some information about the project.\n" +
                "Project name",
                type=str
            )
            self.slugified_name = slugify(self.name)

        if not workspace:
            workspace = self.ask_workspace()

        r = askanna_client.post(self.api_server+"project/", data={
            "name": self.name,
            "workspace": workspace
        })
        if r.status_code == 201:
            click.echo('\nYou have successfully created a new project in AskAnna!')
            return r.json()
        else:
            raise Exception("could not create project")


# read defaults from the environment
default_workspace_suuid = os.getenv('WORKSPACE_SUUID')


@click.command(help=HELP, short_help=SHORT_HELP)
@click.argument("name", required=False)
@click.option('--workspace', '-w', default=default_workspace_suuid, show_default=True)
def cli(name, workspace):
    config = get_config()
    api_server = config['askanna']['remote']
    user = get_user_info(server=api_server)
    project_creator = CreateProject(name=name, api_server=api_server, user=user)
    project_info = project_creator.cli(workspace)

    project_dir = project_creator.slugified_name

    try:
        cookiecreator(
            DEFAULT_DSS_PROJECT,
            no_input=True,
            overwrite_if_exists=False,
            extra_context={
                "project_directory": project_dir,
                "project_name": project_info.get('name'),
                "project_push_target": project_info.get('url')
            }
        )
    except OutputDirExistsException:
        click.echo(
            f"You already have a project directory '{project_dir}'." +
            " If you open the new project in AskAnna, you find instructions about " +
            "how you can push your project to AskAnna.")
    else:
        click.echo(
            f"Open your new local project directory: 'cd {project_dir}'\n"
        )
        # also push the new directory to askanna
        os.chdir(project_dir)
        push(force=True, message="Initial push")

    # finish
    click.echo("\nWe have setup the new project. You can check your project in AskAnna at:")
    click.echo("{project_url}".format(project_url=project_info.get('url')))
