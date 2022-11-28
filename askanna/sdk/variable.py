from typing import List, Optional

from askanna.core.dataclasses.project import Variable
from askanna.gateways.variable import VariableGateway

__all__ = [
    "VariableSDK",
]


class VariableSDK:
    def __init__(self):
        self.variable_gateway = VariableGateway()

    def list(
        self,
        project_suuid: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        ordering: str = "-created",
    ) -> List[Variable]:
        return self.variable_gateway.list(
            project_suuid=project_suuid,
            limit=limit,
            offset=offset,
            ordering=ordering,
        )

    def get(self, variable_suuid: str) -> Variable:
        return self.variable_gateway.detail(variable_suuid=variable_suuid)

    def create(self, project_suuid: str, name: str, value: str, is_masked: bool = False) -> Variable:
        return self.variable_gateway.create(
            project_suuid=project_suuid,
            name=name,
            value=value,
            is_masked=is_masked,
        )

    def change(
        self,
        variable_suuid: str,
        name: Optional[str] = None,
        value: Optional[str] = None,
        is_masked: Optional[bool] = None,
    ) -> Variable:
        return self.variable_gateway.change(
            variable_suuid=variable_suuid,
            name=name,
            value=value,
            is_masked=is_masked,
        )

    def delete(self, variable_suuid: str) -> bool:
        return self.variable_gateway.delete(variable_suuid=variable_suuid)
