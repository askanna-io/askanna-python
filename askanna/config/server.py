import os
import sys
from dataclasses import dataclass
from typing import Dict, Optional

import click

from askanna.config.utils import read_config, store_config
from askanna.settings import (
    DEFAULT_SERVER_CONFIG_PATH,
    DEFAULT_SERVER_REMOTE,
    DEFAULT_SERVER_UI,
)

SERVER_CONFIG_PATH = os.getenv("AA_SERVER_CONFIG_FILE", DEFAULT_SERVER_CONFIG_PATH)
SERVER = os.getenv("AA_SERVER", "default")
DEFAULT_SERVER_CONFIG = {
    "server": {
        "default": {
            "remote": f"{DEFAULT_SERVER_REMOTE}",
            "ui": f"{DEFAULT_SERVER_UI}",
            "token": "",
        },
    }
}


@dataclass
class ServerConfig:
    """Server configuration specification"""

    remote: str
    config_dict: Optional[Dict] = None
    server_config_path: str = SERVER_CONFIG_PATH
    server: str = "default"
    token: str = ""
    ui: str = ""

    @property
    def is_authenticated(self) -> bool:
        if self.token:
            return True
        return False

    def save_server_to_config_file(self):
        self.config_dict = add_or_update_server_in_config_dict(
            self.config_dict, self.server, self.remote, self.token, self.ui
        )
        store_config(self.server_config_path, self.config_dict)

    def logout_and_remove_token(self):
        self.token = ""  # nosec
        self.save_server_to_config_file()


def add_or_update_server_in_config_dict(  # nosec
    config_dict: Optional[Dict], server: str, remote: str, token: str = "", ui: str = ""
) -> Dict:

    server_dict = {
        "remote": remote,
        "ui": ui,
        "token": token,
    }

    if config_dict and config_dict.get("server", {}).get(server):
        config_dict["server"][server].update(server_dict)
    elif config_dict and config_dict.get("server"):
        config_dict["server"].update({server: server_dict})
    else:
        config_dict = {}
        config_dict["server"] = {server: server_dict}

    return config_dict


def load_config(server_config_path: str = SERVER_CONFIG_PATH, server: str = SERVER) -> ServerConfig:
    config_dict = DEFAULT_SERVER_CONFIG

    if os.path.isfile(server_config_path):
        local_config = read_config(server_config_path)
        config_dict.update(local_config)

    server_dict = config_dict.get("server", {}).get(server, {})
    if not server_dict and server != "default":
        click.echo(
            f"Server settings for '{server}' not found. Please try again with a valid server, or add this " "server.",
            err=True,
        )
        sys.exit(1)

    remote = os.getenv("AA_REMOTE", server_dict.get("remote", DEFAULT_SERVER_REMOTE))
    ui = os.getenv("AA_UI", server_dict.get("ui", DEFAULT_SERVER_UI))
    token = os.getenv("AA_TOKEN", server_dict.get("token", ""))

    return ServerConfig(
        config_dict=config_dict,
        server_config_path=server_config_path,
        server=server,
        remote=remote,
        ui=ui,
        token=token,
    )


config: ServerConfig = load_config()
