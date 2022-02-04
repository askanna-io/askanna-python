import os
import sys
from typing import Dict

import click
import requests
import yaml

try:
    from yaml import CSafeDumper as SafeDumper
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: no cover
    from yaml import SafeDumper
    from yaml import SafeLoader as SafeLoader


def read_config(path: str) -> Dict:
    """
    Reading existing config or return default dict
    """
    try:
        with open(os.path.expanduser(path), "r") as f:
            return yaml.load(f, Loader=SafeLoader) or {}
    except FileNotFoundError:
        click.echo(f"Cannot find the config file: {os.path.expanduser(path)}", err=True)
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
    with open(path, "w") as f:
        f.write(yaml.dump(config, Dumper=SafeDumper))


def scan_config_in_path(path: str = ""):
    """
    Look for file `askanna.yml` in parent directories
    """
    filename = "askanna.yml"
    project_configfile = ""

    if not path:
        path = os.getcwd()

    # first check whether we already can find in the current workdir
    if contains_configfile(path, filename):
        project_configfile = os.path.join(path, filename)
    else:
        # traverse up all directories untill we find an askanna.yml file
        split_path = os.path.split(path)
        # in any other cases, look in parent directories
        while split_path[1] != "":
            if contains_configfile(split_path[0], filename):
                project_configfile = os.path.join(split_path[0], filename)
                break
            split_path = os.path.split(split_path[0])
    return project_configfile


def contains_configfile(path: str, filename: str = "askanna.yml") -> bool:
    return os.path.isfile(os.path.join(path, filename))


def read_config_from_url(url: str) -> Dict:
    """
    Get config from URL and return it as dict
    """
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        click.echo(f"Cannot open URL: {url}", err=True)
        sys.exit(1)

    if not r.headers.get("content-type") == "application/octet-stream":
        click.echo(f"The URL '{url}' does not return an expected YAML config", err=True)
        sys.exit(1)

    try:
        return yaml.load(r.content, Loader=SafeLoader) or {}
    except yaml.scanner.ScannerError as e:
        click.echo("Error reading YAML content due to:", err=True)
        click.echo(e.problem, err=True)
        click.echo(e.problem_mark, err=True)
        sys.exit(1)
