import json
import sys
from typing import List, Optional, Union

import click

from askanna.config import config
from askanna.core.dataclasses.job import Job
from askanna.core.dataclasses.project import Project
from askanna.core.dataclasses.run import Run
from askanna.core.dataclasses.variable import Variable
from askanna.core.dataclasses.workspace import Workspace
from askanna.core.push import push
from askanna.sdk.job import JobSDK
from askanna.sdk.project import ProjectSDK
from askanna.sdk.run import RunSDK
from askanna.sdk.variable import VariableSDK
from askanna.sdk.workspace import WorkspaceSDK


def make_option_list_string_for_question(
    list_items: Union[List[Workspace], List[Project], List[Job], List[Run], List[Variable]],
    name_with_suuid: bool = False,
) -> str:
    """From a list of instance items, create a string with the name and optionally suuid of each instance.

    Args:
        list_items (list): a list of intance items. Instance items can be Workspace, Project, Job, Run or Variable.
        name_with_suuid (bool, optional): Boolean if the SUUID should be included in the string. Defaults to False.

    Returns:
        str: a string with the name and optionally suuid of each instance where each instance is on a new line as a
             numbered list.
    """
    list_str = ""
    for idx, item in enumerate(list_items, start=1):
        if name_with_suuid:
            name = f"{item.name} ({item.suuid})" if item.name else item.suuid
        else:
            name = item.name if item.name else item.suuid
        if idx < 10 and len(list_items) >= 10:
            list_str += "%d.  %s\n" % (idx, name)
        else:
            list_str += "%d. %s\n" % (idx, name)

    return list_str


def ask_which_workspace(question: Optional[str] = None) -> Workspace:
    """
    Determine which workspace should be used to perform an action
    """
    workspace_sdk = WorkspaceSDK()
    workspace_list = workspace_sdk.list(number_of_results=99)

    if len(workspace_list) == 0:
        click.echo("This request doesn't return any workspaces. Did you create a workspace?", err=True)
        sys.exit(0)
    elif len(workspace_list) == 1:
        workspace = workspace_list[0]
    else:
        question = question or "Which workspace do you want to select?"
        list_str = make_option_list_string_for_question(workspace_list)

        if workspace_sdk.list_total_count and workspace_sdk.list_total_count > len(workspace_list):
            list_str += (
                f"\nNote: the {len(workspace_list):,} most recent workspaces of {workspace_sdk.list_total_count:,} "
                "workspaces are in the list.\n"
            )

        selected_workspace = click.prompt(
            "\n" + question + "\n\n" + list_str + "\n" + "Please enter the workspace number",
            type=click.Choice([str(i + 1) for i in range(len(workspace_list))]),
            show_choices=False,
        )

        workspace = workspace_list[int(selected_workspace) - 1]

    click.echo(f"Selected workspace: {workspace.name}")
    return workspace


def ask_which_project(question: Optional[str] = None, workspace_suuid: Optional[str] = None) -> Project:
    """
    Determine which project should be used to perform an action
    """
    project_sdk = ProjectSDK()
    project_list = project_sdk.list(workspace_suuid=workspace_suuid, number_of_results=99)

    if len(project_list) == 0:
        click.echo("This request doesn't return any projects. Did you create a project?", err=True)
        sys.exit(0)
    elif len(project_list) == 1:
        project = project_list[0]
    else:
        question = question or "Which project do you want to select?"
        list_str = make_option_list_string_for_question(project_list)

        if project_sdk.list_total_count and project_sdk.list_total_count > len(project_list):
            list_str += (
                f"\nNote: the {len(project_list):,} most recent projects of {project_sdk.list_total_count:,} "
                "projects are in the list.\n"
            )

        selected_project = click.prompt(
            "\n" + question + "\n\n" + list_str + "\n" + "Please enter the project number",
            type=click.Choice([str(i + 1) for i in range(len(project_list))]),
            show_choices=False,
        )

        project = project_list[int(selected_project) - 1]

    click.echo(f"Selected project: {project.name}")
    return project


def ask_which_job(question: Optional[str] = None, project_suuid: Optional[str] = None) -> Job:
    """
    Determine which job should be used to perform an action
    """
    job_sdk = JobSDK()
    job_list = job_sdk.list(project_suuid=project_suuid, number_of_results=99)

    if len(job_list) == 0:
        click.echo(
            "This request doesn't return any jobs. Did you push code with an askanna.yml config file?", err=True
        )
        sys.exit(0)
    elif len(job_list) == 1:
        job = job_list[0]
    else:
        question = question or "Which job do you want to select?"
        list_str = make_option_list_string_for_question(job_list)

        if job_sdk.list_total_count and job_sdk.list_total_count > len(job_list):
            list_str += (
                f"\nNote: the {len(job_list):,} most recent jobs of {job_sdk.list_total_count:,} jobs are in the "
                "list.\n"
            )

        selected_job = click.prompt(
            "\n" + question + "\n\n" + list_str + "\n" + "Please enter the job number",
            type=click.Choice([str(i + 1) for i in range(len(job_list))]),
            show_choices=False,
        )

        job = job_list[int(selected_job) - 1]

    click.echo(f"Selected job: {job.name}")
    return job


def ask_which_run(question: Optional[str] = None, job_suuid: Optional[str] = None) -> Run:
    """
    Determine which job should be used to perform an action
    """
    run_sdk = RunSDK()
    run_list = run_sdk.list(job_suuid=job_suuid, number_of_results=99)

    if len(run_list) == 0:
        click.echo("This request doesn't return any runs. Did you start a run?")
        sys.exit(0)
    elif len(run_list) == 1:
        run = run_list[0]
    else:
        question = question or "Which run do you want to select?"
        list_str = make_option_list_string_for_question(run_list, name_with_suuid=True)

        if run_sdk.list_total_count and run_sdk.list_total_count > len(run_list):
            list_str += (
                f"\nNote: the {len(run_list):,} most recent runs of {run_sdk.list_total_count:,} runs are in the "
                "list.\n"
            )

        selected_run = click.prompt(
            "\n" + question + "\n\n" + list_str + "\n" + "Please enter the run number",
            type=click.Choice([str(i + 1) for i in range(len(run_list))]),
            show_choices=False,
        )

        run = run_list[int(selected_run) - 1]

    click.echo(f"Selected run: {run.suuid}")
    return run


def ask_which_variable(question: Optional[str] = None, project_suuid: Optional[str] = None) -> Variable:
    """
    Determine which variable should be used to perform an action
    """
    variable_sdk = VariableSDK()
    variable_list = variable_sdk.list(project_suuid=project_suuid, number_of_results=99)

    if len(variable_list) == 0:
        click.echo("This request doesn't return any variables. Did you create a variable?", err=True)
        sys.exit(0)
    elif len(variable_list) == 1:
        variable = variable_list[0]
    else:
        question = question or "Which variable do you want to select?"
        list_str = make_option_list_string_for_question(variable_list)

        if variable_sdk.list_total_count and variable_sdk.list_total_count > len(variable_list):
            list_str += (
                f"\nNote: the {len(variable_list):,} most recent variables of {variable_sdk.list_total_count:,} "
                "variables are in the list.\n"
            )

        selected_variable = click.prompt(
            "\n" + question + "\n\n" + list_str + "\n" + "Please enter the variable number",
            type=click.Choice([str(i + 1) for i in range(len(variable_list))]),
            show_choices=False,
        )

        variable = variable_list[int(selected_variable) - 1]

    click.echo(f"Selected variable: {variable.name}")
    return variable


def determine_project_for_run_request(
    project_suuid: Optional[str] = None,
    workspace_suuid: Optional[str] = None,
) -> Project:
    if not project_suuid:
        project_suuid = config.project.project_suuid

    # Still if there is no project_suuid found, we will ask which project to use
    if project_suuid:
        project = ProjectSDK().get(project_suuid=project_suuid)
        click.echo(f"Selected project: {project.name}")
        return project
    else:
        if not workspace_suuid:
            workspace = ask_which_workspace(question="From which workspace do you want to run a job?")
            workspace_suuid = workspace.suuid

        return ask_which_project(
            question="From which project do you want to run a job?",
            workspace_suuid=workspace_suuid,
        )


def job_run_request(
    job_suuid: Optional[str] = None,
    job_name: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    data: Optional[str] = None,
    data_file: Optional[str] = None,
    push_code: bool = False,
    project_suuid: Optional[str] = None,
    workspace_suuid: Optional[str] = None,
):
    json_data = None
    if data and data_file:
        click.echo("Cannot use both --data and --data-file.", err=True)
        sys.exit(1)
    elif data:
        json_data = json.loads(data)
    elif data_file:
        with open(data_file) as json_file:
            json_data = json.load(json_file)

    if json_data and not type(json_data) == dict:
        click.echo("The data cannot be processes becaused it's not in a JSON format.", err=True)
        sys.exit(1)

    if push_code:
        push(overwrite=True, description=description)

    if not job_suuid and not project_suuid:
        project = determine_project_for_run_request(project_suuid, workspace_suuid)
        project_suuid = project.suuid

    if job_suuid:
        pass
    elif job_name:
        job_name = job_name.strip()
        try:
            job = JobSDK().get_job_by_name(job_name=job_name, project_suuid=project_suuid)
            job_suuid = job.suuid
        except Exception as e:
            click.echo(e)
            sys.exit(1)
    else:
        job = ask_which_job(
            question="Which job do you want to run?",
            project_suuid=project_suuid,
        )

        if not click.confirm(f"\nDo you want to run the job '{job.name}'?", abort=False):
            click.echo(f"\nAborted! Not running job '{job.name}'.")
            sys.exit(0)
        else:
            click.echo("")

        job_suuid = job.suuid

    try:
        run = JobSDK().run_request(
            job_suuid=job_suuid,
            data=json_data,
            name=name,
            description=description,
        )
    except Exception as e:
        click.echo(e)
        sys.exit(1)
    else:
        click.echo(f"Succesfully started a new run for job '{run.job.name}' in AskAnna with SUUID " f"'{run.suuid}'.")
