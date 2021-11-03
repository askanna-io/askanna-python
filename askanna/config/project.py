from dataclasses import dataclass
import re
from typing import Dict

from askanna.config.utils import read_config, scan_config_in_path


@dataclass
class PushTarget:
    url: str = ''
    http_scheme: str = ''
    host: str = ''
    project_suuid: str = ''
    workspace_suuid: str = ''


@dataclass
class ProjectConfig:
    config_dict: Dict
    project_config_path: str = ''
    push_target: PushTarget = PushTarget()
    project_suuid: str = ''
    workspace_suuid: str = ''


def extract_push_target(push_target: str) -> PushTarget:
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

    if not matches:
        raise ValueError(f"The push target '{push_target}' is not valid. Please check the documentation to read "
                         "more about the push target: https://docs.askanna.io/code/#push-target")

    matches_dict = matches.groupdict()

    return PushTarget(
        url=push_target,
        http_scheme=matches_dict['http_scheme'],
        host=matches_dict['askanna_host'],
        workspace_suuid=matches_dict['workspace_suuid'],
        project_suuid=matches_dict['project_suuid'],
    )


def load_config(project_config_path: str = '') -> ProjectConfig:
    if not project_config_path:
        project_config_path = scan_config_in_path()

    project_config = {}
    push_target = PushTarget()
    workspace_suuid = ''
    project_suuid = ''

    if project_config_path:
        project_config = read_config(project_config_path)

    push_target_str = project_config.get('push-target')
    if push_target_str:
        push_target = extract_push_target(push_target_str)
        workspace_suuid = push_target.workspace_suuid
        project_suuid = push_target.project_suuid

    return ProjectConfig(
        config_dict=project_config,
        project_config_path=project_config_path,
        push_target=push_target,
        workspace_suuid=workspace_suuid,
        project_suuid=project_suuid,
    )


config: ProjectConfig = load_config()
