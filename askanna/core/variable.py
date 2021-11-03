"""
Management of variables in AskAnna
This is the class which act as gateway to the API of AskAnna
"""
import sys
import click

from askanna.core.apiclient import client
from askanna.core.dataclasses import Variable


class VariableGateway:
    def __init__(self, *args, **kwargs):
        self.client = client
        self.project = None
        self.base_url = self.client.base_url + "variable/"

    def list(self, project_suuid: str = None) -> list:
        if project_suuid:
            # build url to select for project only
            url = f"{self.client.base_url}project/{project_suuid}/variables/"
        else:
            url = self.base_url

        r = self.client.get(url)
        if r.status_code != 200:
            click.echo("We cannot find variables for you")
            sys.exit(1)

        variables = [Variable(**var) for var in r.json()]

        return variables

    def detail(self, suuid: str) -> Variable:
        url = f"{self.base_url}{suuid}/"
        r = self.client.get(url)
        return Variable(**r.json())

    def create(self, name: str, value: str, is_masked: bool, project_suuid: str):
        url = self.base_url
        r = self.client.create(url, json={
            "name": name,
            "value": value,
            "is_masked": is_masked,
            "project": project_suuid
        })
        if r.status_code == 201:
            return Variable(**r.json()), True

        return None, False

    def change(self, suuid: str, name: str = None, value: str = None,
               is_masked: bool = None) -> Variable:
        url = f"{self.base_url}{suuid}/"

        variable = {}
        if name:
            variable.update({"name": name})
        if value:
            variable.update({"value": value})
        if is_masked:
            variable.update({"is_masked": is_masked})

        if variable:
            # emit update request (PATCH)
            r = self.client.patch(
                url,
                json=variable
            )
        else:
            click.echo("Nothing to change for this variable. You did not provide a name, value or is_masked to change "
                       "for this variable", err=True)
            sys.exit(1)

        # show success or failure
        if r.status_code == 200:
            variable_name = r.json().get('name')
            click.echo(f"You have successfully changed the variable: '{variable_name}'")
        else:
            click.echo("Something went wrong while changing the variable", err=True)
            sys.exit(1)
        return Variable(**r.json())

    def delete(self, suuid: str) -> bool:
        url = f"{self.base_url}{suuid}/"
        r = self.client.delete(url)
        return r.status_code == 204
