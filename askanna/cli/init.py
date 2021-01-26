import click
import os
import yaml

from askanna.core import client as askanna_client
from askanna.core.utils import get_config

HELP = """
This command will allow you to create an AskAnna project in your current directory
"""

SHORT_HELP = "Create a project in the current directory"


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
    def __init__(self, name=None, user=None):
        self.config = get_config()
        self.api_server = self.config['askanna']['remote']
        self.name = name
        self.user = user or get_user_info(server=self.api_server)

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
                "\n{name}, you are a member of multiple workspaces. ".format(
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

        if click.confirm("Do you want to create a project '{project}' in '{workspace}'?".format(
                         project=self.name,
                         workspace=selected_workspace['title']
                         ), abort=True):
            click.echo("Thank you for the information. Anna will continue creating the project.")

        return selected_workspace['suuid']

    def cli(self, workspace: str = None, description: str = None):
        if not self.name:
            click.echo("Hi {name_user}! It is time to create a new project in AskAnna. ".format(
                name_user=self.user.get("name")
            ) +
                "We start with some information about the project.")
            self.name = click.prompt("Project name", type=str)

            if not description:
                description = click.prompt("Project description", type=str, default="",
                                           show_default=False)

        if not workspace:
            workspace = self.ask_workspace()

        r = askanna_client.post(self.api_server+"project/", data={
            "name": self.name,
            "workspace": workspace,
            "description": description
        })
        if r.status_code == 201:
            click.echo('\nYou have successfully created a new project in AskAnna!')
            return r.json()
        else:
            raise Exception("We could not create the project.")


@click.command(help=HELP, short_help=SHORT_HELP)
@click.argument("name", required=False)
@click.option("--workspace", "-w", envvar="WORKSPACE_SUUID", show_default=True,
              help="Workspace SUUID where you want to create the project")
@click.option("--description", "-d",
              help="Description of the project")
def cli(name, workspace, description):
    cwd = os.getcwd()
    askanna_project_file = os.path.join(cwd, "askanna.yml")
    if os.path.exists(askanna_project_file):
        click.echo("This directory already has an 'askanna.yml' file. If you continue, we will "
                   "create a new project in AskAnna.")
        click.echo("But, we will not update your 'askanna.yml' file with the push-target of the "
                   "new project. If you continue, you need to add the push-target yourself.\n")
        click.confirm("Do you want to continue without updating the 'askanna.yml'?", abort=True)

    project_creator = CreateProject(name=name)
    project_info = project_creator.cli(workspace, description)

    if not os.path.exists(askanna_project_file):
        with open(askanna_project_file, 'w') as pf:
            pf.write(yaml.dump({"push-target": project_info['url']}, indent=2))

    # finish
    click.echo("\nCheck your project in AskAnna at:")
    click.echo("{project_url}".format(project_url=project_info['url']))
    click.echo("\nAs a first step you can configure your first job for this project in the `askanna.yml` file. "
               "Ones you are done, you can easily push your code to askanna via:\n"
               "\n" "  askanna push\n" "\n"
               "Success with your project!")
