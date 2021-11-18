import collections
import datetime
import ipaddress
import mimetypes
import os
import uuid
from typing import Any, Dict, List, Tuple
from zipfile import ZipFile

import click
import croniter
import igittigitt
import pytz
import requests
import tzlocal
from email_validator import EmailNotValidError, validate_email

from askanna import __version__ as askanna_version
from askanna.settings import PYPI_PROJECT_URL

StorageUnit = collections.namedtuple("StorageUnit", ["B", "KiB", "MiB", "GiB", "TiB", "PiB"])

diskunit = StorageUnit(B=1, KiB=1024 ** 1, MiB=1024 ** 2, GiB=1024 ** 3, TiB=1024 ** 4, PiB=1024 ** 5)

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


def flatten(t):
    return [item for sublist in t for item in sublist]


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


# Zip the files that matches the filter from given directory
def zip_files_in_dir(directory_path: str, zip_file: ZipFile, ignore_file: str = None) -> None:
    files = get_files_in_dir(directory_path=directory_path, ignore_file=ignore_file)
    # Iterate over all the files and zip them
    for file in sorted(files):
        zip_file.write(file)


def get_files_in_dir(directory_path: str, ignore_file: str = None) -> set:
    file_list = set()

    ignore_parser = igittigitt.IgnoreParser()
    if ignore_file:
        ignore_parser.parse_rule_files(os.path.dirname(ignore_file), os.path.basename(ignore_file))

    # Iterate over all the files in directory
    for root, _, files in os.walk(directory_path):
        for file in files:
            # Create complete filepath of file in directory
            file_path = os.path.join(root, file)
            if file_path.startswith("./"):
                file_path = file_path[2:]

            # can we add this file to the collection?
            if not ignore_parser.match(file_path):
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


def file_type(path):
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


def getProjectPackages(project, offset=0, limit=1):
    from askanna.config import config
    from askanna.core.apiclient import client

    r = client.get(
        "{api_server}/v1/project/{project_suuid}/packages/?offset={offset}&limit={limit}".format(
            api_server=config.server.remote,
            project_suuid=project.short_uuid,
            offset=offset,
            limit=limit,
        )
    )
    if not r.status_code == 200:
        return []

    return r.json()


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
        "notifications",
        "project",
        "push-target",
        "timezone",
        "variables",
        "worker",
    )

    overlapping_with_reserved_keys = list(set(config.keys()).intersection(set(reserved_keys)))
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


def validate_yml_environments(config: Dict, jobname=None) -> bool:
    """
    Validate the environment definitions (if defined)
    """
    # Do we have a global `environment` defined?
    environment = config.get("environment")
    if environment:
        if not isinstance(environment, dict):
            if jobname:
                click.echo(
                    f"Invalid definition of `environment` found in job `{jobname}`:\n"
                    f"environment: {environment}\n"
                    "\n"
                    "For environment documentation: https://docs.askanna.io/environments/",
                    err=True,
                )
            else:
                click.echo(
                    "Invalid definition of `environment` found:\n"
                    f"environment: {environment}\n"
                    "\n"
                    "For environment documentation: https://docs.askanna.io/environments/",
                    err=True,
                )
            return False
        else:
            # make sure we have at least the `image` defined
            image = environment.get("image")
            if not image:
                click.echo(
                    "`image` was not defined in the `environment`:\n"
                    f"environment: {environment}\n"
                    "\n"
                    "For environment documentation: https://docs.askanna.io/environments/",
                    err=True,
                )
                return False

    return True


def validate_yml_notifications(config: Dict, jobname=None) -> bool:
    """
    Validate the definition of `notifications` in global and job
    """
    notifications = config.get("notifications")
    if notifications and not isinstance(notifications, dict):
        if jobname:
            click.echo(
                f"Invalid definition of `notifications` found in job `{jobname}`:\n"
                f"notifications: {notifications}"
                "\n"
                "For notifications documentation: https://docs.askanna.io/jobs/notifications/",
                err=True,
            )
        else:
            click.echo(
                "Invalid `notifications` setting found:"
                f"notifications: {notifications}"
                "\n"
                "For notifications documentation: https://docs.askanna.io/jobs/notifications/",
                err=True,
            )
        return False
    elif notifications and isinstance(notifications, dict):
        # check for values of `all` and `error`, both should be dicts
        noti_all = notifications.get("all")
        noti_error = notifications.get("error")
        if any(
            [
                noti_all and not isinstance(noti_all, dict),
                noti_error and not isinstance(noti_error, dict),
            ]
        ):
            if jobname:
                click.echo(
                    f"Invalid definition of `notifications` found in job `{jobname}`:\n"
                    f"notifications: {notifications}"
                    "\n"
                    "For notifications documentation: https://docs.askanna.io/jobs/notifications/",
                    err=True,
                )
            else:
                click.echo(
                    "Invalid `notifications` setting found:\n"
                    f"notifications: {notifications}"
                    "\n"
                    "For notifications documentation: https://docs.askanna.io/jobs/notifications/",
                    err=True,
                )
            return False

        # proceed with validation of the content
        # assume we can get values out of all/email and error/email
        noti_all_values = notifications.get("all", {}).get("email", [])
        noti_error_values = notifications.get("error", {}).get("email", [])

        all_email = sorted(
            flatten(
                list(
                    map(
                        lambda x: x.split(","),
                        noti_all_values + noti_error_values,
                    )
                )
            )
        )
        for value in all_email:
            if value.startswith("${") and value.endswith("}"):
                # we found a variable not subsituted yet
                continue
            if value in ["workspace admins", "workspace members"]:
                # valid addresees
                continue

            # validate on actual content of the value whether it is an e-mail address or not
            try:
                validate_email(value)
            except EmailNotValidError:
                click.echo(
                    "Invalid `notifications/email` found:\n" f"{value}" "\n",
                    err=True,
                )
                return False

    return True


def validate_askanna_yml(config):
    """
    Given an dictionary of askanna.yml validate each component
    """
    jobs = config.items()

    global_timezone = config.get("timezone")
    # validate the global timezone
    if global_timezone:
        if global_timezone not in pytz.all_timezones:
            click.echo(
                "Invalid timezone setting found in askanna.yml:\n" + f"timezone: {global_timezone}",
                err=True,
            )
            return False
        timezone_checked = True  # used later, so we only print a warning message about the timezone once
    else:
        timezone_checked = False  # used later, so we only print a warning message about the timezone once

    # validate whether the global environment definitions are correct
    if not validate_yml_environments(config):
        return False

    # validate for global notification settings
    if not validate_yml_notifications(config):
        return False

    # validate jobs names
    if not validate_yml_job_names(config):
        return False

    for jobname, job in jobs:
        if isinstance(job, dict):
            if not validate_yml_environments(job, jobname=jobname):
                return False
            if not validate_yml_notifications(job, jobname=jobname):
                return False

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
            timezone = job.get("timezone")
            if timezone and timezone not in pytz.all_timezones:
                click.echo(
                    f"Invalid timezone setting found in job `{jobname}`:\n" + f"timezone: {timezone}",
                    err=True,
                )
                return False

            # validate the schedule
            schedule = job.get("schedule")
            if schedule:
                for cron_line, parsed in parse_cron_schedule(schedule):
                    if not parsed:
                        click.echo(
                            f"Invalid schedule definition `{cron_line}` found in job `{jobname}`",
                            err=True,
                        )
                        return False

                if not timezone and not global_timezone and not timezone_checked:
                    timezone_local = getLocalTimezone()
                    if timezone_local != "UTC":
                        click.echo(  # noqa
                            f"""
By default, the AskAnna platform uses time zone UTC. Your current time zone is {timezone_local}.
To use your local time zone for scheduling jobs in this project, add the next line to your config in `askanna.yml`:

timezone: {timezone_local}

For more information, read the documentation: https://docs.askanna.io/jobs/create-job/#time-zone
"""
                        )
                    timezone_checked = True
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


def transform_value(value: Any) -> Tuple[Any, bool]:
    """
    Transform values in support datatypes
    """
    if object_fullname(value) == "range":
        return list(value), True

    return value, False


def prepare_and_validate_value(value: Any) -> Tuple[Any, bool]:
    """
    Validate value and if necessary transform values in support datatypes
    """
    if validate_value(value):
        return value, True

    # Try to transform the value
    value, transform = transform_value(value)
    if transform:
        return value, True

    return value, False


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
                if v:
                    v, valid = prepare_and_validate_value(v)
                    if valid:
                        labels.append(labelclass(name=k, value=v, dtype=translate_dtype(v)))
                    else:
                        click.echo(
                            f"AskAnna cannot store this datatype. Label {k} with value {v} not stored.",
                            err=True,
                        )
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


def content_type_file_extension(content_type: str) -> str:
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
