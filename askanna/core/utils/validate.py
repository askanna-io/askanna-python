from typing import Dict, List, Union

import click
import croniter
import pytz
from email_validator import EmailNotValidError, validate_email
from tzlocal import get_localzone


def flatten(t):
    return [item for sublist in t for item in sublist]


def validate_cron_line(cron_line: str) -> bool:
    """
    We validate the cron expression with croniter
    """
    return croniter.croniter.is_valid(cron_line)


def parse_cron_line(cron_line: str) -> Union[str, None]:
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
        valid_keys = {"minute", "hour", "day", "month", "weekday"}
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
                    timezone_local = get_localzone()
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
