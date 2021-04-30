# -*- coding: utf-8 -*-
import click
import sys

from askanna import job as aa_job
from askanna import project as aa_project
from askanna import workspace as aa_workspace
from askanna.core.dataclasses import Job, Project, Workspace


def ask_which_workspace(question: str = None) -> Workspace:
    """
    Determine which workspace should be used to perform an action
    """
    workspace_list = aa_workspace.list()
    # if logged in user is only member of one workspace, we don't have to as which workspace
    if len(workspace_list) == 0:
        click.echo("It seems that you are not a member of a workspace. Please check your account.", err=True)
        sys.exit(0)
    elif len(workspace_list) == 1:
        workspace = workspace_list[0]
    else:
        list_str = ""
        for idx, workspace in enumerate(workspace_list, start=1):
            list_str += "%d. %s\n" % (idx, workspace.name)

        if not question:
            question = "Which workspace do you want to select?"

        selection = click.prompt(
            "\n" + question + "\n\n" + list_str + "\n"
            + "Please enter the workspace number",
            type=click.Choice([str(i + 1) for i in range(len(workspace_list))]),
            show_choices=False
        )

        workspace = workspace_list[int(selection) - 1]

    click.echo(f"Selected workspace: {workspace.name}")
    return workspace


def ask_which_project(question: str = None, workspace_suuid: str = None) -> Project:
    """
    Determine which project should be used to perform an action
    """
    project_list = aa_project.list(workspace_suuid=workspace_suuid)

    if len(project_list) == 0:
        click.echo("In this workspace you don't have access to any project. Please check your account or the selected "
                   "workspace.", err=True)
        sys.exit(0)

    list_str = ""
    for idx, project in enumerate(project_list, start=1):
        list_str += "%d. %s\n" % (idx, project.name)

    if not question:
        question = "Which project do you want to select?"

    selection = click.prompt(
        "\n" + question + "\n\n" + list_str + "\n"
        + "Please enter the project number",
        type=click.Choice([str(i + 1) for i in range(len(project_list))]),
        show_choices=False
    )

    project = project_list[int(selection) - 1]
    click.echo(f"Selected project: {project.name}")

    return project


def ask_which_job(question: str = None, project_suuid: str = None) -> Job:
    """
    Determine which job should be used to perform an action
    """
    job_list = aa_job.list(project_suuid=project_suuid)

    if len(job_list) == 0:
        click.echo("In this project you don't have access to any job. Please check if you have pushed your code or "
                   "check the selected project.", err=True)
        sys.exit(0)

    list_str = ""
    for idx, job in enumerate(job_list, start=1):
        list_str += "%d. %s\n" % (idx, job.name)

    if not question:
        question = "Which job do you want to select?"

    selected_job = click.prompt(
        "\n" + question + "\n\n" + list_str + "\n"
        + "Please enter the job number",
        type=click.Choice([str(i + 1) for i in range(len(job_list))]),
        show_choices=False
    )

    job = job_list[int(selected_job) - 1]
    click.echo(f"Selected job: {job.name}")

    return job
