import pytest


@pytest.fixture
def project_detail() -> dict:
    return {
        "uuid": "08c7cdf5-be3c-4263-b06a-c70bfed66a05",
        "short_uuid": "1234-1234-1234-1234",
        "name": "a project",
        "description": "a project description",
        "workspace": {
            "relation": "workspace",
            "name": "a workspace",
            "uuid": "2fbfbc98-083a-42a7-890c-0d95cc1ab903",
            "short_uuid": "1S6G-K3fI-visU-LKac",
        },
        "package": {
            "uuid": "6af7721c-7b15-4ddc-9f9b-de92826dbfcf",
            "short_uuid": "3FqG-if1Z-Gd2s-uYvq",
            "name": "a-project_f8cbd1bd38a544f1819b8e9b957e933c.zip",
        },
        "notifications": {"all": {"email": []}, "error": {"email": []}},
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
        "is_member": False,
        "created_by": {
            "uuid": "726f6262-6572-7440-6173-6b616e6e6121",
            "short_uuid": "3Tw1-jp9H-FjQw-8PYY",
            "name": "Robbert",
        },
        "visibility": "PUBLIC",
        "created": "2021-06-29T08:16:05.554963Z",
        "modified": "2022-09-19T08:08:59.744557Z",
        "url": "https://askanna.eu/1S6G-K3fI-visU-LKac/project/GZFT-EmyJ-CJ5V-kYKM",
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
        "next": "https://api.askanna.eu/v1/project/?limit=1&offset=1",
        "previous": None,
        "results": [project_new_detail],
    }


@pytest.fixture
def project_new_detail() -> dict:
    return {
        "uuid": "a43ea3f4-ccfb-46e2-a94b-c0b52dea6d1f",
        "short_uuid": "abcd-abcd-abcd-abcd",
        "name": "a new project",
        "description": "description new project",
        "workspace": {
            "relation": "workspace",
            "name": "a workspace",
            "uuid": "2fbfbc98-083a-42a7-890c-0d95cc1ab903",
            "short_uuid": "1S6G-K3fI-visU-LKac",
        },
        "package": {"uuid": None, "short_uuid": None, "name": None},
        "notifications": {},
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
        "created_by": {
            "uuid": "726f6262-6572-7440-6173-6b616e6e6121",
            "short_uuid": "3Tw1-jp9H-FjQw-8PYY",
            "name": "Robbert",
        },
        "visibility": "PUBLIC",
        "created": "2022-10-19T07:54:07.334220Z",
        "modified": "2022-10-19T07:54:07.334273Z",
        "url": "https://askanna.eu/1S6G-K3fI-visU-LKac/project/abcd-abcd-abcd-abcd",
    }
