from typing import List, Union

import click
import requests

from askanna import __version__ as askanna_version
from askanna.core.dataclasses.run import Label
from askanna.core.utils.object import (
    get_type,
    object_fullname,
    prepare_and_validate_value,
)
from askanna.settings import PYPI_PROJECT_URL


def update_available() -> bool:
    """
    Check whether most recent release of AskAnna on PyPI is newer than the AskAnna version in use. If a newer version
    is available, return a info message with update instructions.
    """
    try:
        r = requests.get(PYPI_PROJECT_URL)
    except requests.exceptions.ConnectionError:
        return False
    except requests.exceptions.HTTPError:
        return False
    else:
        if r.status_code == 200:
            pypi_info = r.json()
        else:
            return False

    if askanna_version == pypi_info["info"]["version"]:
        return False
    else:
        click.echo("[INFO] A newer version of AskAnna is available. Update via: pip install -U askanna")
        return True


def make_label_list(label: Union[str, list, dict]) -> List[Label]:
    label_list = []

    if not label:
        return label_list

    # If label is of type string or list, then convert it to tag
    if isinstance(label, str):
        label_list.append(Label(name=label, value=None, type="tag"))
    elif isinstance(label, list):
        for name in label:
            label_list.append(Label(name=name, value=None, type="tag"))
    elif isinstance(label, dict):
        for name, value in label.items():
            if value is None:
                label_list.append(Label(name=name, value=None, type="tag"))
            else:
                value, valid = prepare_and_validate_value(value)
                if valid:
                    label_list.append(Label(name=name, value=value, type=get_type(value)))
                else:
                    click.echo(
                        f"AskAnna cannot store the datatype '{object_fullname(value)}'. Label not stored for '{name}' "
                        f"with value '{value}'.",
                        err=True,
                    )

    return label_list
