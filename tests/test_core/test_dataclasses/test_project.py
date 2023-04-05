from askanna.core.dataclasses.project import Project
from tests.utils import str_to_datetime


def test_project(project_detail):
    project = Project.from_dict(project_detail.copy())

    assert project.suuid == project_detail["suuid"]
    assert project.name == project_detail["name"]
    assert project.description == project_detail["description"]
    assert project.created_at == str_to_datetime(project_detail["created_at"])
    assert project.modified_at == str_to_datetime(project_detail["modified_at"])

    assert str(project) == "Project: a project (1234-1234-1234-1234)"
