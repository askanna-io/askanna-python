import os
import glob
import confuse

from pathlib import Path


from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

CONFIG_USERCONFIG_FILE = "~/.config/askanna.yml"
CONFIG_USERHOME_FILE = "~/.askanna.yml"

def init_checks():
    create_config(CONFIG_USERCONFIG_FILE)
    create_config(CONFIG_USERHOME_FILE)


def create_config(location: str):
    expanded_path = os.path.expanduser(location)
    folder = os.path.dirname(expanded_path)
    filename = os.path.basename(expanded_path)

    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    if not os.path.exists(expanded_path):
        Path(expanded_path).touch()


def update_available(silent_fail=True):
    """
    Check whether most recent Gitlab release of askanna_cli is newer than the
    askanna_cli version in use. If a newer version is available, return a
    link to the release on Gitlab, otherwise return ``None``.
    """
    try:
        # FIXME: some code to check the release on Gitlab
        a = None
        return a
    except Exception:
        if not silent_fail:
            raise

        # Don't let this interfere with askanna_cli usage
        return None

def check_for_project():
    """
    Performs a check if we are operating within a project folder. When
    we wish to perform a deploy action, we want to be on the same
    level with the ``setup.py`` to be able to package the file.
    """
    cwd = os.getcwd()

    pyfiles = glob.glob('*.py')

    # look for the setup.py file
    if 'setup.py' in pyfiles:
        return True

    else:
        return False

def get_config() -> dict:
    config = load(open(os.path.expanduser("~/.askanna.yml"), 'r'), Loader=Loader)
    return config

def store_config(config):
    original_config = get_config()
    original_config.update(**config)
    output = dump(original_config, Dumper=Dumper) 
    print(output)
    return output
