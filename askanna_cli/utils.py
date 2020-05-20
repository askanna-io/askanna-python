import os
import glob
import mimetypes
import collections

from pathlib import Path
import zipfile
from zipfile import ZipFile

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
        while split_path[1] is not "":
            print(split_path[0])
            if contains_configfile(split_path[0]):
                project_configfile = os.path.join(
                    split_path[0],
                    "askanna.yml"
                )
                break
            split_path = os.path.split(split_path[0])
    return project_configfile

def read_config(path:str) -> dict:
    return load(open(os.path.expanduser(path), 'r'), Loader=Loader)

def contains_configfile(path:str, filename:str="askanna.yml") -> bool:
    return os.path.isfile(
        os.path.join(path, filename)
    )

def get_config() -> dict:
    config = read_config(CONFIG_USERHOME_FILE)
    project_config = scan_config_in_path()
    if project_config:
        config.update(**read_config(project_config))
    return config

def store_config(config):
    original_config = get_config()
    original_config.update(**config)
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

