"""
Management of variables in AskAnna
"""
from askanna.core.dataclasses import Variable
from askanna.core.variable import VariableGateway


def list(project_suuid: str = None) -> list:
    g = VariableGateway()
    return g.list(project_suuid=project_suuid)


def detail(suuid: str) -> Variable:
    g = VariableGateway()
    return g.detail(suuid=suuid)


def create(name: str, value: str, is_masked: bool, project_suuid: str):
    g = VariableGateway()
    return g.create(name=name, value=value, is_masked=is_masked, project_suuid=project_suuid)


def change(suuid: str, name: str = None, value: str = None,
           is_masked: bool = None) -> Variable:
    g = VariableGateway()
    return g.change(suuid=suuid, name=name, value=value, is_masked=is_masked)


def delete(suuid: str) -> bool:
    g = VariableGateway()
    return g.delete(suuid=suuid)
