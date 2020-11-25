"""
Management of variables in AskAnna
This is the class which act as gateway to the API of AskAnna
"""
from . import client
from dataclasses import dataclass
import datetime
import uuid
import sys


@dataclass
class Variable:
    name: str
    value: str
    short_uuid: str
    uuid: uuid.UUID
    is_masked: bool
    created: datetime.datetime
    modified: datetime.datetime
    project: dict


class VariableGateway:
    def __init__(self, *args, **kwargs):
        self.client = client
        self.project = None
        self.cache = {}
        self.base_url = self.client.config.remote + "variable/"

    def list(self, project=None, show_masked=False):
        url = self.base_url
        if project:
            # build url to select for project only
            url = "{}{}/{}/{}".format(
                self.client.config.remote,
                "project",
                project,
                "variables"
            )
        r = self.client.get(url)
        if r.status_code != 200:
            print("We cannot find variables for you")
            sys.exit(1)

        variables = [Variable(**var) for var in r.json()]
        self.cache = variables
        return variables

    def detail(self, short_uuid) -> dict:
        url = "{}{}/".format(self.base_url, short_uuid)
        r = self.client.get(url)
        return Variable(**r.json())

    def change(self, short_uuid, variable):
        url = "{}{}/".format(self.base_url, short_uuid)

        # emit update request (PATCH)
        r = self.client.patch(
            url,
            json={
                "name": variable.name,
                "value": variable.value,
                "is_masked": variable.is_masked
            }
        )

        # show success or failure
        if r.status_code == 200:
            variable_name = r.json().get('name')
            print("You have successfully changed the variable: '{variable_name}'".format(variable_name=variable_name))
            sys.exit(0)
        else:
            print("Something went wrong while changing the variable")
            sys.exit(1)
        return Variable(**r.json())

    def delete(self, short_uuid):
        url = "{}{}/".format(self.base_url, short_uuid)
        r = self.client.delete(url)
        return r.status_code == 204

    def create(self, name, value, masked, project):
        url = self.base_url
        r = self.client.create(url, json={
            "name": name,
            "value": value,
            "is_masked": masked,
            "project": project
        })
        if r.status_code == 201:
            return Variable(**r.json()), True

        return None, False
