
import collections
import glob
import mimetypes
import os
import re

from pathlib import Path
from zipfile import ZipFile

import requests
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

CONFIG_USERHOME_FILE = "~/.askanna.yml"

StorageUnit = collections.namedtuple('StorageUnit',
                                     [
                                         'B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB'
                                     ])

diskunit = StorageUnit(B=1, KiB=1024**1, MiB=1024**2, GiB=1024**3, TiB=1024**4, PiB=1024**5)


def init_checks():
    create_config(CONFIG_USERHOME_FILE)


def create_config(location: str):
    expanded_path = os.path.expanduser(location)
    folder = os.path.dirname(expanded_path)

    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    if not os.path.exists(expanded_path):
        Path(expanded_path).touch()

        # write initial config since it didn't exist
        with open(expanded_path, 'w') as f:
            config = store_config({
                'askanna': {
                    'remote': 'https://beta-api.askanna.eu/v1/'
                }
            })
            f.write(config)


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
    level with the ``askanna.yml`` to be able to package the file.
    """
    pyfiles = glob.glob('*.yml')

    # look for the setup.py file
    if 'askanna.yml' in pyfiles:
        return True
    else:
        return False


def scan_config_in_path(cwd=None):
    """
    Look for askanna.yml in parent directories
    """
    if not cwd:
        cwd = os.getcwd()
    project_configfile = ""
    # first check whether we already can find in the current workdir
    if contains_configfile(cwd):
        project_configfile = os.path.join(cwd, "askanna.yml")
    else:
        # traverse up all directories untill we find an askanna.yml file
        split_path = os.path.split(cwd)
        # in any other cases, look in parent directories
        while split_path[1] != "":
            if contains_configfile(split_path[0]):
                project_configfile = os.path.join(
                    split_path[0],
                    "askanna.yml"
                )
                break
            split_path = os.path.split(split_path[0])
    return project_configfile


def read_config(path: str) -> dict:
    """
    Reading existing config or return default dict
    """
    return load(open(os.path.expanduser(path), 'r'), Loader=Loader) or {}


def contains_configfile(path: str, filename: str = "askanna.yml") -> bool:
    return os.path.isfile(
        os.path.join(path, filename)
    )


def get_config() -> dict:
    init_checks()
    config = read_config(CONFIG_USERHOME_FILE) or {}
    project_config = scan_config_in_path()
    if project_config:
        config.update(**read_config(project_config))

    # overwrite the AA remote if AA_REMOTE is set in the environment
    is_remote_set = os.getenv('AA_REMOTE')
    if is_remote_set:
        config['askanna'] = config.get('askanna', {})
        config['askanna']['remote'] = is_remote_set

    # overwrite the user token if AA_TOKEN is set in the environment
    is_token_set = os.getenv('AA_TOKEN')
    if is_token_set:
        config['auth'] = config.get('auth', {})
        config['auth']['token'] = is_token_set

    # overwrite the project token if set in the env
    is_project_set = os.getenv('PROJECT_UUID')
    if is_project_set:
        config['project'] = config.get('project', {})
        config['project']['uuid'] = is_project_set

    return config


def store_config(new_config):
    original_config = get_config()
    original_config.update(**new_config)
    output = dump(original_config, Dumper=Dumper)
    return output


# Zip the files from given directory that matches the filter
def zipFilesInDir(dirName, zipFileName, filter):
    os.chdir(dirName)
    # create a ZipFile object
    with ZipFile(zipFileName, mode='w') as zipObj:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk('.'):
            for filename in filenames:
                if filter(filename):
                    # create complete filepath of file in directory
                    filePath = os.path.join(folderName, filename)
                    # Add file to zip
                    zipObj.write(filePath)


def zipAFile(zipObj: ZipFile, dirpath: str, filepath: str, prefixdir: str) -> None:
    # create complete filepath of file in directory
    filePath = os.path.join(dirpath, filepath)
    # Add file to zip
    zipObj.write(filePath)


def zipFolder(zipObj: ZipFile, dirpath: str, prefixdir: str):
    os.chdir(dirpath)
    # Iterate over all the files in directory
    for folderName, subfolders, filenames in os.walk('.'):
        for filename in filenames:
            # create complete filepath of file in directory
            filePath = os.path.join(folderName, filename)
            # Add file to zip
            zipObj.write(filePath, os.path.join(prefixdir, filePath))


def zipPaths(zipObj: ZipFile, paths: list, cwd: str):
    for targetloc in paths:
        if targetloc.startswith('/'):
            prefixdir = targetloc
        else:
            prefixdir = targetloc
            targetloc = os.path.join(cwd, targetloc)

        # check for existence

        if not os.path.exists(targetloc):
            print(targetloc, "does not exists ... skipping")
            continue

        if os.path.isdir(targetloc):
            zipFolder(zipObj, targetloc, prefixdir=prefixdir)
        else:
            # we got a file?
            zipAFile(zipObj, dirpath=os.path.dirname(targetloc),
                     filepath=os.path.basename(targetloc), prefixdir=prefixdir)


def _file_type(path):
    """Mimic the type parameter of a JS File object.
    Resumable.js uses the File object's type attribute to guess mime type,
    which is guessed from file extention accoring to
    https://developer.mozilla.org/en-US/docs/Web/API/File/type.
    Parameters
    ----------
    path : str
        The path to guess the mime type of
    Returns
    -------
    str
        The inferred mime type, or '' if none could be inferred
    """
    type_, _ = mimetypes.guess_type(path)
    # When no type can be inferred, File.type returns an empty string
    return '' if type_ is None else type_


def string_expand_variables(strings: list) -> list:
    var_matcher = re.compile(r"\$\{(?P<MYVAR>[\w\-]+)\}")
    for idx, line in enumerate(strings):
        matches = var_matcher.findall(line)
        for m in matches:
            line = line.replace("${"+m+"}", os.getenv(m.strip()))
        strings[idx] = line
    return strings


def getProjectInfo(project_suuid, api_server, token):
    r = requests.get(
        "{api_server}project/{project_suuid}/".format(
            api_server=api_server,
            project_suuid=project_suuid
        ),
        headers={
            'user-agent': 'askanna-cli/0.2.0',
            'Authorization': 'Token {token}'.format(
                token=token
            )
        }
    )
    if not r.status_code == 200:
        return {}

    return r.json()


def getProjectPackages(project, api_server, token, offset=0, limit=1):
    r = requests.get(
        "{api_server}project/{project_suuid}/packages/?offset={offset}&limit={limit}".format(
            api_server=api_server,
            project_suuid=project['short_uuid'],
            offset=offset,
            limit=limit
        ),
        headers={
            'user-agent': 'askanna-cli/0.2.0',
            'Authorization': 'Token {token}'.format(
                token=token
            )
        }
    )
    if not r.status_code == 200:
        return []

    return r.json()
