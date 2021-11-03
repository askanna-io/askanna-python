from dataclasses import dataclass
import os
import sys
from typing import Dict


import click

from askanna.config.utils import read_config, store_config
from askanna.settings import (
    DEFAULT_SERVER_CONFIG_PATH,
    DEFAULT_SERVER_REMOTE,
    DEFAULT_SERVER_UI,
)


SERVER_CONFIG_PATH = os.getenv('AA_SERVER_CONFIG_FILE', DEFAULT_SERVER_CONFIG_PATH)
SERVER = os.getenv('AA_SERVER', 'default')
DEFAULT_SERVER_CONFIG = {
    'server': {
        'default': {
            'remote': f'{DEFAULT_SERVER_REMOTE}',
            'ui': f'{DEFAULT_SERVER_UI}',
            'token': '',
        },
    }
}


@dataclass
class ServerConfig:
    """
    Server configuration specification
    """

    remote: str
    config_dict: Dict = None
    server_config_path: str = SERVER_CONFIG_PATH
    server: str = 'default'
    token: str = ''
    ui: str = ''

    @property
    def is_authenticated(self) -> bool:
        if self.token:
            return True
        return False

    def save_server_to_config_file(self):
        self.config_dict = add_or_update_server_in_config_dict(
            self.config_dict,
            self.server,
            self.remote,
            self.token,
            self.ui
        )
        store_config(self.server_config_path, self.config_dict)

    def logout_and_remove_token(self):
        self.token = ''
        self.save_server_to_config_file()


def add_or_update_server_in_config_dict(
    config_dict: Dict,
    server: str,
    remote: str,
    token: str = '',
    ui: str = ''
) -> Dict:

    server_dict = {
        'remote': remote,
        'ui': ui,
        'token': token,
    }

    if config_dict.get('server', {}).get(server):
        config_dict['server'][server].update(server_dict)
    elif config_dict.get('server'):
        config_dict['server'].update({server: server_dict})
    else:
        config_dict['server'] = {server: server_dict}

    return config_dict


def update_to_new_config(config_dict : Dict, server_config_path : str, server : str):
    """
    Updates the config file because the AskAnna team changed the config file setup
    This function can be removed in the future.
    """

    remote = config_dict['askanna'].get('remote', '')
    remote = remote.replace('/v1/', '')

    ui = ''
    token = ''

    if remote == 'https://beta-api.askanna.eu':
        ui = 'https://beta.askanna.eu'

    del config_dict['askanna']

    if config_dict.get('auth'):
        token = config_dict['auth'].get('token', '')

    try:
        del config_dict['auth']
    except:  # noqa
        pass

    config_dict = add_or_update_server_in_config_dict(config_dict, server, remote, token, ui)

    store_config(server_config_path, config_dict)
    click.echo('[INFO] We updated your AskAnna config file to support the latest features')

    return read_config(server_config_path)


def load_config(server_config_path : str = SERVER_CONFIG_PATH, server : str = SERVER) -> ServerConfig:
    config_dict = DEFAULT_SERVER_CONFIG

    if os.path.isfile(server_config_path):
        local_config = read_config(server_config_path)
        config_dict.update(local_config)

        # Automatically updates the config file because of new config setup
        # Next section can be removed in a future version
        if config_dict.get('askanna'):
            config_dict = update_to_new_config(config_dict, server_config_path, server)

    server_dict = config_dict.get('server', {}).get(server, {})
    if not server_dict and server != 'default':
        click.echo(f"Server settings for '{server}' not found. Please try again with a valid server, or add this "
                   "server.", err=True)
        sys.exit(1)

    remote = os.getenv('AA_REMOTE', server_dict.get('remote', DEFAULT_SERVER_REMOTE))
    ui = os.getenv('AA_UI', server_dict.get('ui', DEFAULT_SERVER_UI))
    token = os.getenv('AA_TOKEN', server_dict.get('token', ''))

    return ServerConfig(
        config_dict=config_dict,
        server_config_path=server_config_path,
        server=server,
        remote=remote,
        ui=ui,
        token=token,
    )


config: ServerConfig = load_config()
