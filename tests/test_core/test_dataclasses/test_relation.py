from askanna.core.dataclasses.relation import (
    BaseRelation,
    CreatedByRelation,
    CreatedByWithAvatarRelation,
    JobRelation,
    PackageRelation,
    PayloadRelation,
    ProjectRelation,
    RunRelation,
    UserRelation,
    WorkspaceRelation,
)


def test_base_relation():
    data = {
        "relation": "workspace",
        "suuid": "1234-1234-1234-1234",
        "name": "a workspace",
    }
    relation = BaseRelation.from_dict(data.copy())

    assert relation.relation == data["relation"]
    assert relation.suuid == data["suuid"]
    assert relation.name == data["name"]


def test_workspace_relation():
    data = {
        "relation": "workspace",
        "suuid": "1234-1234-1234-1234",
        "name": "a workspace",
    }
    relation = WorkspaceRelation.from_dict(data.copy())

    assert relation.relation == data["relation"]
    assert relation.suuid == data["suuid"]
    assert relation.name == data["name"]


def test_project_relation():
    data = {
        "relation": "project",
        "suuid": "1234-1234-1234-1234",
        "name": "a project",
    }
    relation = ProjectRelation.from_dict(data.copy())

    assert relation.relation == data["relation"]
    assert relation.suuid == data["suuid"]
    assert relation.name == data["name"]


def test_package_relation():
    data = {
        "relation": "package",
        "suuid": "1234-1234-1234-1234",
        "name": "a package",
    }
    relation = PackageRelation.from_dict(data.copy())

    assert relation.relation == data["relation"]
    assert relation.suuid == data["suuid"]
    assert relation.name == data["name"]


def test_job_relation():
    data = {
        "relation": "job",
        "suuid": "1234-1234-1234-1234",
        "name": "a job",
    }
    relation = JobRelation.from_dict(data.copy())

    assert relation.relation == data["relation"]
    assert relation.suuid == data["suuid"]
    assert relation.name == data["name"]


def test_run_relation():
    data = {
        "relation": "run",
        "suuid": "1234-1234-1234-1234",
        "name": "a run",
    }
    relation = RunRelation.from_dict(data.copy())

    assert relation.relation == data["relation"]
    assert relation.suuid == data["suuid"]
    assert relation.name == data["name"]


def test_user_relation():
    data = {
        "relation": "user",
        "suuid": "1234-1234-1234-1234",
    }
    relation = UserRelation.from_dict(data.copy())

    assert relation.relation == data["relation"]
    assert relation.suuid == data["suuid"]


def test_created_by_relation():
    data = {
        "relation": "created_by",
        "suuid": "1234-1234-1234-1234",
        "name": "a user",
        "job_title": "a job title",
        "role": {
            "name": "a role",
            "code": "WQ",
        },
        "status": "a status",
    }
    relation = CreatedByRelation.from_dict(data.copy())

    assert relation.relation == data["relation"]
    assert relation.suuid == data["suuid"]
    assert relation.name == data["name"]
    assert relation.job_title == data["job_title"]
    assert relation.role.name == data["role"]["name"]
    assert relation.role.code == data["role"]["code"]
    assert relation.status == data["status"]


def test_created_by_with_avatar_relation():
    data = {
        "relation": "created_by",
        "suuid": "1234-1234-1234-1234",
        "name": "a user",
        "job_title": "a job title",
        "role": {
            "name": "a role",
            "code": "WQ",
        },
        "status": "a status",
        "avatar": {
            "url_1": "https://example.com/1",
            "url_2": "https://example.com/2",
        },
    }
    relation = CreatedByWithAvatarRelation.from_dict(data.copy())

    assert relation.relation == data["relation"]
    assert relation.suuid == data["suuid"]
    assert relation.name == data["name"]
    assert relation.job_title == data["job_title"]
    assert relation.role.name == data["role"]["name"]
    assert relation.role.code == data["role"]["code"]
    assert relation.status == data["status"]
    assert relation.avatar["url_1"] == data["avatar"]["url_1"]
    assert relation.avatar["url_2"] == data["avatar"]["url_2"]


def test_payload_relation():
    data = {
        "relation": "payload",
        "suuid": "1234-1234-1234-1234",
        "name": "a payload",
        "size": 1234,
        "lines": 1234,
    }
    relation = PayloadRelation.from_dict(data.copy())

    assert relation.relation == data["relation"]
    assert relation.suuid == data["suuid"]
    assert relation.name == data["name"]
    assert relation.size == data["size"]
    assert relation.lines == data["lines"]
