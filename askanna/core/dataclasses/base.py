import datetime
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Label:
    name: str
    value: Any
    type: str

    def __str__(self):
        return f"{self.name}: {self.value} [type: {self.type}]"

    def to_dict(self, yes=True) -> Dict:
        return {"name": self.name, "value": self.value, "type": self.type}


@dataclass
class User:
    suuid: str
    name: str
    email: str
    is_active: bool
    date_joined: datetime.datetime
    last_login: datetime.datetime
