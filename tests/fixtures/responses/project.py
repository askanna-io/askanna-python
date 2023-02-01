import pytest


@pytest.fixture
def project_detail() -> dict:
    return {
        "suuid": "1234-1234-1234-1234",
        "name": "a project",
        "description": "a project description",
        "visibility": "PUBLIC",
        "workspace": {
            "relation": "workspace",
            "suuid": "1S6G-K3fI-visU-LKac",
            "name": "a workspace",
        },
        "package": {
            "relation": "package",
            "suuid": "3FqG-if1Z-Gd2s-uYvq",
            "name": "a-project_f8cbd1bd38a544f1819b8e9b957e933c.zip",
        },
        "created_by": {
            "relation": "user",
            "suuid": "3Tw1-jp9H-FjQw-8PYY",
        },
        "is_member": False,
        "permission": {
            "workspace.me.view": True,
            "workspace.me.edit": False,
            "workspace.me.remove": False,
            "workspace.info.view": True,
            "workspace.info.edit": False,
            "workspace.remove": False,
            "workspace.project.list": True,
            "workspace.project.create": False,
            "workspace.people.list": False,
            "workspace.people.invite.create": False,
            "workspace.people.invite.remove": False,
            "workspace.people.invite.resend": False,
            "workspace.people.edit": False,
            "workspace.people.remove": False,
            "project.me.view": True,
            "project.info.view": True,
            "project.info.edit": False,
            "project.remove": False,
            "project.code.list": True,
            "project.code.create": False,
            "project.job.list": True,
            "project.job.create": False,
            "project.job.edit": False,
            "project.job.remove": False,
            "project.variable.list": True,
            "project.variable.create": False,
            "project.variable.edit": False,
            "project.variable.remove": False,
            "project.run.list": True,
            "project.run.create": False,
            "project.run.edit": False,
            "project.run.remove": False,
            "askanna.me": True,
            "askanna.admin": False,
            "askanna.member": False,
            "askanna.workspace.create": False,
        },
        "created": "2021-06-29T08:16:05.554963Z",
        "modified": "2022-09-19T08:08:59.744557Z",
    }


@pytest.fixture
def project_list(project_detail) -> dict:
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [project_detail],
    }


@pytest.fixture
def project_list_limit(project_new_detail) -> dict:
    return {
        "count": 18,
        "next": "https://api.askanna.eu/v1/project/?cursor=567&page_size=1",
        "previous": None,
        "results": [project_new_detail],
    }


@pytest.fixture
def project_new_detail() -> dict:
    return {
        "suuid": "abcd-abcd-abcd-abcd",
        "name": "a new project",
        "description": "description new project",
        "visibility": "PUBLIC",
        "workspace": {
            "relation": "workspace",
            "suuid": "1S6G-K3fI-visU-LKac",
            "name": "a workspace",
        },
        "package": None,
        "created_by": {
            "relation": "user",
            "suuid": "3Tw1-jp9H-FjQw-8PYY",
        },
        "is_member": True,
        "permission": {
            "askanna.me": True,
            "askanna.admin": False,
            "askanna.member": True,
            "askanna.workspace.create": True,
            "workspace.me.view": True,
            "workspace.me.edit": True,
            "workspace.me.remove": True,
            "workspace.info.view": True,
            "workspace.info.edit": True,
            "workspace.remove": True,
            "workspace.project.list": True,
            "workspace.project.create": True,
            "workspace.people.list": True,
            "workspace.people.invite.create": True,
            "workspace.people.invite.remove": True,
            "workspace.people.invite.resend": True,
            "workspace.people.edit": True,
            "workspace.people.remove": True,
            "project.me.view": True,
            "project.info.view": True,
            "project.info.edit": True,
            "project.remove": True,
            "project.code.list": True,
            "project.code.create": True,
            "project.job.list": True,
            "project.job.create": True,
            "project.job.edit": True,
            "project.job.remove": True,
            "project.variable.list": True,
            "project.variable.create": True,
            "project.variable.edit": True,
            "project.variable.remove": True,
            "project.run.list": True,
            "project.run.create": True,
            "project.run.edit": True,
            "project.run.remove": True,
        },
        "created": "2022-10-19T07:54:07.334220Z",
        "modified": "2022-10-19T07:54:07.334273Z",
    }
