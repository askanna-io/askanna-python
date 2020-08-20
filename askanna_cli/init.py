import click
import requests
import os
import yaml
from askanna_cli.utils import get_config

HELP = """
This command will allow you to create a project
"""

SHORT_HELP = "Create an AskAnna project"


def find_workspace(api_server: str, headers: dict) -> list:
    """
        Find all workspaces where the user is part of and enumerate them
    """
    workspaces = []
    r = requests.get('{}workspace'.format(api_server), headers=headers)

    for workspace in r.json():
        workspaces.append({
            'suuid': workspace['short_uuid'],
            'title': workspace['title']
        })
    for idx, workspace in enumerate(workspaces, start=1):
        print("%d. %s" % (idx, workspace['title']))
    return workspaces


class CreateProject:
    def __init__(self, name=None, push_target=None, project_info=None):
        self.name = name,
        self.push_target = push_target,
        self.project_info = project_info

    def cli(self):
        config = get_config()
        token = config['auth']['token']
        api_server = config['askanna']['remote']
        headers = {
            'Authorization': "Token {usertoken}".format(
                usertoken=token
            )
        }
        self.name = click.prompt(
            "Project name ",
            type=str
        )
        workspaces = find_workspace(api_server, headers)
        workspace = click.prompt(

            "Enter which workspace to use "
        )
        selected_workspace = workspaces[int(workspace)-1]

        self.project_info = requests.post(api_server+"project/", headers=headers, data={
            "name": self.name,
            "workspace": selected_workspace['suuid']
        })
        if self.project_info.status_code == 201:
            self.project_info = self.project_info.json()
            click.echo('You have successfully created a new project and connected your existing directory to AskAnna.')
            return self.name, self.project_info
        else:
            raise Exception("could not create project")

    def create_file(self):
        cwd = os.getcwd()
        project_info = self.project_info
        self.push_target = project_info['url']
        askanna_project_file = os.path.join(cwd, "askanna.yml")
        if not os.path.exists(askanna_project_file):
            with open(askanna_project_file, 'w') as pf:
                pf.write(yaml.dump({
                    "push_target": self.push_target,
                    "first job":
                        {"job": ""
                         }
                }, indent=2))


@click.command(help=HELP, short_help=SHORT_HELP)
def cli():
    project_creator = CreateProject()
    project_name, project_info = project_creator.cli()

    if project_name:
        project_creator.create_file()
    click.echo("As a first step you can configure your first job for this project in the `askanna.yml` file. "
               "Ones you are done, you can easily push your code to askanna via:\n"
               "\n" "  askanna push\n" "\n"
               "Success with your project!")
