import os
import sys
from typing import Dict

import click
import yaml
from yaml import dump, load

try:
    from yaml import CDumper as Dumper, CLoader as Loader
except ImportError:  # pragma: no cover
    from yaml import Dumper, Loader


def read_config(path: str) -> Dict:
    """
    Reading existing config or return default dict
    """
    try:
        with open(os.path.expanduser(path), 'r') as f:
            return load(f, Loader=Loader) or {}
    except FileNotFoundError:
        click.echo(f'Cannot find the config file: {os.path.expanduser(path)}', err=True)
        sys.exit(1)
    except TypeError as e:
        click.echo(e, err=True)
        sys.exit(1)
    except yaml.scanner.ScannerError as e:
        click.echo("Error reading 'askanna.yml' due to:", err=True)
        click.echo(e.problem, err=True)
        click.echo(e.problem_mark, err=True)
        sys.exit(1)


def store_config(path, config: Dict):
    with open(path, 'w') as f:
        f.write(dump(config, Dumper=Dumper))


def scan_config_in_path(path: str = ''):
    """
    Look for file `askanna.yml` in parent directories
    """
    filename = 'askanna.yml'
    project_configfile = ''

    if not path:
        path = os.getcwd()

    # first check whether we already can find in the current workdir
    if contains_configfile(path, filename):
        project_configfile = os.path.join(path, filename)
    else:
        # traverse up all directories untill we find an askanna.yml file
        split_path = os.path.split(path)
        # in any other cases, look in parent directories
        while split_path[1] != '':
            if contains_configfile(split_path[0], filename):
                project_configfile = os.path.join(split_path[0], filename)
                break
            split_path = os.path.split(split_path[0])
    return project_configfile


def contains_configfile(path: str, filename: str = 'askanna.yml') -> bool:
    return os.path.isfile(os.path.join(path, filename))
