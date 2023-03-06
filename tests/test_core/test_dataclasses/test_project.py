from datetime import datetime, timezone

from askanna.core.dataclasses.project import Project


def test_project(project_detail):
    project = Project.from_dict(project_detail.copy())

    assert project.suuid == project_detail["suuid"]
    assert project.name == project_detail["name"]
    assert project.description == project_detail["description"]
    assert project.created_at == datetime.strptime(project_detail["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=timezone.utc
    )
    assert project.modified_at == datetime.strptime(project_detail["modified_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=timezone.utc
    )

    assert str(project) == "Project: a project (1234-1234-1234-1234)"
