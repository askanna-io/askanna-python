import pytest


@pytest.fixture
def workspace_detail() -> dict:
    return {
        "suuid": "1234-1234-1234-1234",
        "name": "test-workspace",
        "description": "Here you can add some info about the workspace",
        "visibility": "PRIVATE",
        "created_by": {
            "relation": "membership",
            "suuid": "7FzS-oPBG-BIi5-lTeL",
            "name": "Robbert",
            "job_title": "Founder AskAnna",
            "role": {"name": "Workspace Admin", "code": "WA"},
            "status": "active",
            "avatar": {
                "icon": "https://cdn-api.askanna.eu/files/avatars/ee78fc794bee886999ed5ffe3b68/avatar_3b68_icon.png",
                "small": "https://cdn-api.askanna.eu/files/avatars/ee78f80ee886999ed5ffe3b68/avatar_86999ed_small.png",
                "medium": "https://cdn-api.askanna.eu/files/avatars/ee7e8999ed5ffe3b68/avatar_ee78fc7f8b68_medium.png",
                "large": "https://cdn-api.askanna.eu/files/avatars/ee78fc7f80a94be899efffe3b68/avatar_e88e8_large.png",
            },
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
        "created_at": "2020-04-01T09:44:11.853000Z",
        "modified_at": "2022-09-19T08:47:40.214291Z",
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
        "next": "https://api.askanna.eu/v1/workspace/?cursor=567&page_size=1",
        "previous": None,
        "results": [
            workspace_new_detail,
        ],
    }


@pytest.fixture
def workspace_new_detail() -> dict:
    return {
        "suuid": "4buD-tVhI-emHj-QXCY",
        "name": "a new workspace",
        "description": "description new workspace",
        "visibility": "PUBLIC",
        "created_by": {
            "relation": "membership",
            "suuid": "7FzS-oPBG-BIi5-lTeL",
            "name": "Robbert",
            "job_title": "Founder AskAnna",
            "role": {"name": "Workspace Admin", "code": "WA"},
            "status": "active",
            "avatar": {
                "icon": "https://cdn-api.askanna.eu/files/avatars/ee78fc794bee886999ed5ffe3b68/avatar_3b68_icon.png",
                "small": "https://cdn-api.askanna.eu/files/avatars/ee78f80ee886999ed5ffe3b68/avatar_86999ed_small.png",
                "medium": "https://cdn-api.askanna.eu/files/avatars/ee7e8999ed5ffe3b68/avatar_ee78fc7f8b68_medium.png",
                "large": "https://cdn-api.askanna.eu/files/avatars/ee78fc7f80a94be899efffe3b68/avatar_e88e8_large.png",
            },
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
        "created_at": "2022-10-18T07:31:47.803088Z",
        "modified_at": "2022-10-18T07:31:47.803123Z",
    }
