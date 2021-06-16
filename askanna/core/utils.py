import collections
import datetime
import glob
import ipaddress
import mimetypes
import os
from pathlib import Path
import re
import sys
import requests
from typing import Any, List, Callable, Union
import uuid
from zipfile import ZipFile

import click
import croniter
import pytz
import tzlocal
import yaml
from yaml import load, dump

from askanna import __version__ as askanna_version
from askanna.settings import (
    CONFIG_FILE_ASKANNA,
    CONFIG_ASKANNA_REMOTE,
    DEFAULT_PROJECT_TEMPLATE,
    PYPI_PROJECT_URL,
)

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


from askanna.core import exceptions


StorageUnit = collections.namedtuple(
    "StorageUnit", ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
)

diskunit = StorageUnit(
    B=1, KiB=1024 ** 1, MiB=1024 ** 2, GiB=1024 ** 3, TiB=1024 ** 4, PiB=1024 ** 5
)

supported_data_types = {
    # primitive types
    "bool": "boolean",
    "int": "integer",
    "float": "float",
    "str": "string",
    # complex types
    "datetime.datetime": "datetime",
    "datetime.time": "time",
    "datetime.date": "date",
    "dict": "dictionary",
    "list": "list",
    "tag": "tag",
}

try:
    import numpy as np  # noqa: F401
except ImportError:
    # do nothing we don't support numpy
    numpy_available = False
else:
    numpy_available = True
    # list taken from https://numpy.org/doc/stable/user/basics.types.html
    numpy_types = {
        "numpy.bool_": "boolean",
        "numpy.intc": "integer",
        "numpy.int_": "integer",
        "numpy.uint": "integer",
        "numpy.short": "integer",
        "numpy.ushort": "integer",
        "numpy.longlong": "integer",
        "numpy.ulonglong": "integer",
        "numpy.half": "float",
        "numpy.float16": "float",
        "numpy.single": "float",
        "numpy.double": "float",
        "numpy.longdouble": "float",
        "numpy.csingle": "float",
        "numpy.cdouble": "float",
        "numpy.clongdouble": "float",
        # more platform specific types
        "numpy.int8": "integer",
        "numpy.int16": "integer",
        "numpy.int32": "integer",
        "numpy.int64": "integer",
        "numpy.uint8": "integer",
        "numpy.uint16": "integer",
        "numpy.uint32": "integer",
        "numpy.uint64": "integer",
        "numpy.intp": "integer",
        "numpy.uintp": "integer",
        "numpy.float32": "float",
        "numpy.float64": "float",
        "numpy.float_": "float",
        # python equivalant of Decimal, convert to float now
        "numpy.complex64": "float",
        "numpy.complex128": "float",
        "numpy.complex_": "float",
        # list type
        "numpy.array": "list",
    }
    supported_data_types.update(**numpy_types)


def object_fullname(o):
    # https://stackoverflow.com/a/2020083
    # o.__module__ + "." + o.__class__.__qualname__ is an example in
    # this context of H.L. Mencken's "neat, plausible, and wrong."
    # Python makes no guarantees as to whether the __module__ special
    # attribute is defined, so we take a more circumspect approach.
    # Alas, the module name is explicitly excluded from __qualname__
    # in Python 3.

    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return o.__class__.__name__  # Avoid reporting __builtin__
    else:
        return module + "." + o.__class__.__name__


def update_available() -> bool:
    """
    Check whether most recent release of AskAnna on PyPI is newer than the AskAnna version in use. If a newer version
    is available, return a info message with update instructions.
    """
    try:
        r = requests.get(PYPI_PROJECT_URL)
    except requests.exceptions.ConnectionError:
        return False
    else:
        if r.status_code == 200:
            pypi_info = r.json()
        else:
            return False

    if askanna_version == pypi_info["info"]["version"]:
        return False
    else:
        click.echo(
            "[INFO] A newer version of AskAnna is available. Update via: pip install -U askanna"
        )
        return True


def check_for_project():
    """
    Performs a check if we are operating within a project folder. When
    we wish to perform a deploy action, we want to be on the same
    level with the `askanna.yml` to be able to package the file.
    """
    pyfiles = glob.glob("*.yml")

    # look for the setup.py file
    if "askanna.yml" in pyfiles:
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
                project_configfile = os.path.join(split_path[0], "askanna.yml")
                break
            split_path = os.path.split(split_path[0])
    return project_configfile


def read_config(path: str) -> dict:
    """
    Reading existing config or return default dict
    """
    try:
        with open(os.path.expanduser(path), "r") as f:
            return load(f, Loader=Loader) or {}
    except FileNotFoundError:
        config_folder = os.path.dirname(CONFIG_FILE_ASKANNA)
        if not os.path.exists(config_folder):
            os.makedirs(config_folder, exist_ok=True)

        Path(CONFIG_FILE_ASKANNA).touch()

        # Write initial config if the config file didn't exist
        config = store_config(CONFIG_ASKANNA_REMOTE)
        with open(CONFIG_FILE_ASKANNA, "w") as f:
            f.write(config)

        return CONFIG_ASKANNA_REMOTE
    except TypeError as e:
        click.echo(e, err=True)
        sys.exit(1)
    except yaml.scanner.ScannerError as e:
        click.echo("Error reading askanna.yml due to:", err=True)
        click.echo(e.problem, err=True)
        click.echo(e.problem_mark, err=True)
        sys.exit(1)


def contains_configfile(path: str, filename: str = "askanna.yml") -> bool:
    return os.path.isfile(os.path.join(path, filename))


def get_config(check_config=True) -> dict:
    config = read_config(CONFIG_FILE_ASKANNA)

    # overwrite the AA remote if AA_REMOTE is set in the environment
    is_remote_set = os.getenv("AA_REMOTE")
    if is_remote_set:
        config["askanna"] = config.get("askanna", {})
        config["askanna"]["remote"] = is_remote_set

    # if askanna remote is not set, add a default remote to the config file
    try:
        config["askanna"]["remote"]
    except KeyError:
        config = store_config(CONFIG_ASKANNA_REMOTE)
        with open(CONFIG_FILE_ASKANNA, "w") as f:
            f.write(config)
        config = read_config(CONFIG_FILE_ASKANNA)

    # overwrite the user token if AA_TOKEN is set in the environment
    is_token_set = os.getenv("AA_TOKEN")
    if is_token_set:
        config["auth"] = config.get("auth", {})
        config["auth"]["token"] = is_token_set

    # set the project template
    config["project"] = config.get("project", {})
    config["project"]["template"] = os.getenv(
        "PROJECT_TEMPLATE_URL", DEFAULT_PROJECT_TEMPLATE
    )

    project_config = scan_config_in_path()
    if project_config:
        config.update(**read_config(project_config))

    if check_config:
        validate_config(config)

    return config


def validate_config(config):
    try:
        config["auth"]["token"]
    except KeyError:
        click.echo(
            "You are not logged in. Please login first via `askanna login`.", err=True
        )
        sys.exit(1)


def store_config(new_config):
    original_config = read_config(CONFIG_FILE_ASKANNA)
    original_config.update(**new_config)
    output = dump(original_config, Dumper=Dumper)
    return output


# Zip the files that matches the filter from given directory
def zip_files_in_dir(
    directory_path: str, zip_file: ZipFile, filter=lambda x: x
) -> None:
    files = get_files_in_dir(directory_path=directory_path, filter=filter)

    # Iterate over all the files and zip them
    for file in sorted(files):
        zip_file.write(file)


def get_files_in_dir(
    directory_path: str, filter: Callable[[str], Union[str, bool]] = lambda x: x
) -> set:
    file_list = set()

    # Iterate over all the files in directory
    for root, _, files in os.walk(directory_path):
        for file in files:
            if filter(file):
                # Create complete filepath of file in directory
                file_path = os.path.join(root, file)
                if file_path.startswith("./"):
                    file_path = file_path[2:]
                file_list.add(file_path)

    return file_list


def zip_paths(paths: List, zip_file: ZipFile, exclude_paths: List = []) -> None:
    files = get_files_in_paths(paths, exclude_paths)

    # Iterate over all the files and zip them
    for file in sorted(files):
        zip_file.write(file)


def get_files_in_paths(paths: List, exclude_paths: List = []) -> set:
    files = set()

    # first filter out empty string paths
    for path in filter(lambda x: len(x), paths):
        # replace asteriks if possible
        if path.startswith("*"):
            path = "." + path[1:]

        if path.endswith("/*"):
            path = path[:-1]

        if not os.path.exists(path):
            click.echo(f"{path} does not exists...skipping")
            continue

        # base folder path and check whether this is in the exclude_list
        base_folder = "/".join(path.split("/")[:2])
        if base_folder in exclude_paths:
            click.echo(
                f"[CONFIG ERROR] '{base_folder}' from '{path}' is on the exclusion list. AskAnna does not allow to "
                "access these files. This path is ignored and we continue with the other paths.",
                err=True,
            )
            continue

        if os.path.isdir(path):
            files.update(get_files_in_dir(path))
        else:  # so, we got a file
            if path.startswith("./"):
                path = path[2:]
            files.add(path)

    return sorted(files)


def create_zip_from_paths(filename: str, paths: List = []) -> None:
    """
    Create a ZipFile on the given `filename` location
    """
    # we exclude the following directories from included into the zip
    exclude_paths = [
        "/",
        "/bin",
        "/dev",
        "/lib",
        "/mnt",
        "/opt",
        "/proc",
        "/usr",
        "/var",
    ]

    with ZipFile(filename, mode="w") as f:
        zip_paths(paths, f, exclude_paths=exclude_paths)


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
    return "" if type_ is None else type_


def getProjectInfo(project_suuid):
    # import the lib functions here, to prevent circular import
    from askanna.core import client
    from askanna.core.config import Config
    from askanna.core.dataclasses import Project

    config = Config()
    r = client.get(
        "{api_server}project/{project_suuid}/".format(
            api_server=config.remote, project_suuid=project_suuid
        ),
    )

    if r.status_code != 200:
        raise exceptions.GetError(
            "{} - Something went wrong while retrieving the "
            "project info: {}".format(r.status_code, r.reason)
        )

    return Project(**r.json())


def getProjectPackages(project, offset=0, limit=1):
    from askanna.core import client
    from askanna.core.config import Config

    config = Config()
    r = client.get(
        "{api_server}project/{project_suuid}/packages/?offset={offset}&limit={limit}".format(
            api_server=config.remote,
            project_suuid=project.short_uuid,
            offset=offset,
            limit=limit,
        )
    )
    if not r.status_code == 200:
        return []

    return r.json()


def extract_push_target(push_target: str):
    """
    Extract push target from the url configured
    Workspace is optional
    """
    if not push_target:
        raise ValueError("Cannot extract push-target if push-target is not set.")
    match_pattern = re.compile(
        r"(?P<http_scheme>https|http):\/\/(?P<askanna_host>[\w\.\-\:]+)\/(?P<workspace_suuid>[\w-]+){0,1}\/{0,1}project\/(?P<project_suuid>[\w-]+)\/{0,1}"  # noqa: E501
    )
    matches = match_pattern.match(push_target)
    matches_dict = matches.groupdict()
    return matches_dict


def validate_cron_line(cron_line: str) -> bool:
    """
    We validate the cron expression with croniter
    """
    return croniter.croniter.is_valid(cron_line)


def parse_cron_line(cron_line: str) -> str:
    """
    parse incoming cron definition
    if it is valid, then return the cron_line, otherwise a None
    """

    if isinstance(cron_line, str):
        # we deal with cron strings
        # first check whether we need to make a "translation" for @strings

        alias_mapping = {
            "@midnight": "0 0 * * *",
            "@yearly": "0 0 1 1 *",
            "@annually": "0 0 1 1 *",
            "@monthly": "0 0 1 * *",
            "@weekly": "0 0 * * 0",
            "@daily": "0 0 * * *",
            "@hourly": "0 * * * *",
        }
        cron_line = alias_mapping.get(cron_line.strip(), cron_line.strip())

    elif isinstance(cron_line, dict):
        # we deal with dictionary
        # first check whether we have valid keys, if one invalid key is found, return None
        valid_keys = set(["minute", "hour", "day", "month", "weekday"])
        invalid_keys = set(cron_line.keys()) - valid_keys
        if len(invalid_keys):
            return None
        cron_line = "{minute} {hour} {day} {month} {weekday}".format(
            minute=cron_line.get("minute", "0"),
            hour=cron_line.get("hour", "0"),
            day=cron_line.get("day", "*"),
            month=cron_line.get("month", "*"),
            weekday=cron_line.get("weekday", "*"),
        )

    if not validate_cron_line(cron_line):
        return None

    return cron_line


def parse_cron_schedule(schedule: List):
    """
    Determine and validate which format the cron defition it has, it can be one of the following:
    - * * * * *  (m, h, d, m, weekday)
    - @annotation (@yearly, @annually, @monthly, @weekly, @daily, @hourly)
    - dict (k,v with: minute,hour,day,month,weekday)
    """

    for cron_line in schedule:
        yield cron_line, parse_cron_line(cron_line)


def validate_yml_job_names(config):
    """
    Within AskAnna, we have several variables reserved and cannot be used for jobnames
    """
    reserved_keys = (
        "askanna",
        "cluster",
        "environment",
        "image",
        "job",
        "project",
        "push-target",
        "timezone",
        "variables",
        "worker",
    )

    overlapping_with_reserved_keys = list(
        set(config.keys()).intersection(set(reserved_keys))
    )
    for overlap_key in overlapping_with_reserved_keys:
        is_dict = isinstance(config.get(overlap_key), dict)
        is_job = is_dict and config.get(overlap_key).get("job")
        if is_dict and is_job:
            # we do find a job definition under the name, so probably a jobdef
            click.echo(
                f"The name `{overlap_key}` cannot be used for a job.\n"
                "This name is used to configure something else in AskAnna.\n"
                f"Invalid job name: {overlap_key}",
                err=True,
            )
            return False
    return True


def validate_yml_schedule(config):
    jobs = config.items()
    global_timezone = config.get("timezone")
    # validate the global timezone
    if global_timezone and global_timezone not in pytz.all_timezones:
        click.echo(
            "Invalid timezone setting found in askanna.yml:\n"
            + f"   timezone: '{global_timezone}'",
            err=True,
        )
        return False

    for _, job in jobs:
        if isinstance(job, dict):
            schedule = job.get("schedule")
            timezone = job.get("timezone")
            if not schedule:
                continue
            # validate the schedule
            for cron_line, parsed in parse_cron_schedule(schedule):
                if not parsed:
                    click.echo(
                        f"Invalid schedule definition found in job `{job}`: {cron_line}",
                        err=True,
                    )
                    return False
            # validate the timezone if set
            if timezone and timezone not in pytz.all_timezones:
                click.echo(
                    f"Invalid timezone found in job: `{job}`: `{timezone}`",
                    err=True,
                )
                return False
    return True


# generation of suuid
def bx_encode(n, alphabet):
    """
    Encodes an integer :attr:`n` in base ``len(alphabet)`` with
    digits in :attr:`alphabet`.

    ::
        # 'ba'
        bx_encode(3, 'abc')
    :param n:            a positive integer.
    :param alphabet:     a 0-based iterable.
    """

    if not isinstance(n, int):
        raise TypeError("an integer is required")

    base = len(alphabet)

    if n == 0:
        return alphabet[0]

    digits = []

    while n > 0:
        digits.append(alphabet[n % base])
        n = n // base

    digits.reverse()
    return "".join(digits)


def str_to_suuid(string, n) -> str:
    return [string[i : i + n] for i in range(0, len(string), n)]


def create_suuid(uuid_obj) -> str:
    """
    Given an uuid4, return the suuid form of it
    """
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    token_length = 16
    group_size = 4
    groups = int(token_length / group_size)

    # Generate a random UUID if not given
    if not uuid_obj:
        uuid_obj = uuid.uuid4()

    # Convert it to a number with the given alphabet,
    # padding with the 0-symbol as needed)
    token = bx_encode(int(uuid_obj.hex, 16), alphabet)
    token = token.rjust(token_length, alphabet[0])

    return "-".join(str_to_suuid(token, group_size)[:groups])


def serialize_numpy_for_json(obj):
    # the o.item() is a generic method on each numpy dtype.
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def json_serializer(obj):
    if isinstance(obj, (datetime.time, datetime.date, datetime.datetime)):
        return obj.isoformat()
    if numpy_available:
        obj = serialize_numpy_for_json(obj)
    return obj


def translate_dtype(value: Any) -> str:
    """
    Return the full name of the type, if not listed, return the typename from the input
    """
    typename = object_fullname(value)

    return supported_data_types.get(typename, typename)


def validate_value(value: Any) -> bool:
    """
    Validate whether the value set is supported
    """

    return object_fullname(value) in supported_data_types


def labels_to_type(label: Any = None, labelclass=collections.namedtuple) -> List:
    # process labels
    labels = []

    # test label type, if it is a string, then convert it to tag
    if isinstance(label, str):
        labels.append(labelclass(name=label, value=None, dtype="tag"))
    elif isinstance(label, list):
        for name in label:
            labels.append(labelclass(name=name, value=None, dtype="tag"))
    elif label:
        for k, v in label.items():
            if v is None:
                labels.append(labelclass(name=k, value=None, dtype="tag"))
            else:
                if v and not validate_value(v):
                    click.echo(
                        f"AskAnna cannot store this datatype. Label {k} with value {v} not stored.",
                        err=True
                    )
                else:
                    labels.append(labelclass(name=k, value=v, dtype=translate_dtype(v)))

    return labels


def isIPAddress(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return False
    return True


def getLocalTimezone() -> str:
    """
    Determine the local timezone name
    """
    return tzlocal.get_localzone().zone


def content_type_file_extension(content_type : str) -> str:
    content_type_file_extension_mapping = {
        "application/csv": ".csv",
        "application/json": ".json",
        "application/pdf": ".pdf",
        "application/vnd.ms-excel": ".xls",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "application/zip": ".zip",
        "image/jpeg": ".jpeg",
        "image/png": ".png",
        "text/plain": ".txt",
        "text/xml": ".xml",
    }

    file_extension = content_type_file_extension_mapping.get(content_type, ".unknown")

    return file_extension
