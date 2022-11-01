import pytest


@pytest.fixture
def workspace_detail() -> dict:
    return {
        "uuid": "695fcc8b-ba8c-4575-a1e0-f0fcfc70a349",
        "short_uuid": "1234-1234-1234-1234",
        "name": "test-workspace",
        "description": "Here you can add some info about the workspace",
        "visibility": "PRIVATE",
        "created_by": {
            "uuid": "726f6262-6572-7440-6173-6b616e6e6121",
            "short_uuid": "3Tw1-jp9H-FjQw-8PYY",
            "name": "Robbert",
        },
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
        "is_member": True,
        "created": "2020-04-01T09:44:11.853000Z",
        "modified": "2022-09-19T08:47:40.214291Z",
        "url": "https://askanna.eu/3Cpy-QMzd-MVko-1rDQ/",
    }


@pytest.fixture
def workspace_list(workspace_detail) -> dict:
    return {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [workspace_detail],
    }


@pytest.fixture
def workspace_list_limit(workspace_new_detail) -> dict:
    return {
        "count": 8,
        "next": "https://api.askanna.eu/v1/workspace/?limit=1&offset=1",
        "previous": None,
        "results": [
            workspace_new_detail,
        ],
    }


@pytest.fixture
def workspace_new_detail() -> dict:
    return {
        "uuid": "978420cf-e42e-4c3b-95fb-405f1e2f6a88",
        "short_uuid": "4buD-tVhI-emHj-QXCY",
        "name": "a new workspace",
        "description": "description new workspace",
        "visibility": "PUBLIC",
        "created_by": {
            "uuid": "726f6262-6572-7440-6173-6b616e6e6121",
            "short_uuid": "3Tw1-jp9H-FjQw-8PYY",
            "name": "Robbert",
        },
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
        "is_member": True,
        "created": "2022-10-18T07:31:47.803088Z",
        "modified": "2022-10-18T07:31:47.803123Z",
        "url": "https://askanna.eu/4buD-tVhI-emHj-QXCY/",
    }
