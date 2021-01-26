"""
Management of variables in AskAnna
"""

from askanna.core.dataclasses import Variable
from askanna.core.variable import VariableGateway


def list(project: str = None):
    g = VariableGateway()
    return g.list(project=project)


def detail(short_uuid: str) -> Variable:
    g = VariableGateway()
    return g.detail(short_uuid=short_uuid)


def create(name: str, value: str, is_masked: bool, project: str):
    g = VariableGateway()
    return g.create(name=name, value=value, is_masked=is_masked, project=project)


def change(short_uuid: str, name: str = None, value: str = None,
           is_masked: bool = None) -> Variable:
    g = VariableGateway()
    return g.change(short_uuid=short_uuid, name=name, value=value, is_masked=is_masked)


def delete(short_uuid: str) -> bool:
    g = VariableGateway()
    return g.delete(short_uuid=short_uuid)
