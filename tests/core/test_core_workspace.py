import unittest

import responses
from responses.matchers import json_params_matcher

from askanna.core.apiclient import client
from askanna.core.workspace import WorkspaceGateway

a_sample_workspace_response = {
    "uuid": "695fcc8b-ba8c-4575-a1e0-f0fcfc70a349",
    "short_uuid": "3Cpy-QMzd-MVko-1rDQ",
    "name": "AskAnna",
    "description": "",
    "visibility": "PUBLIC",
    "created_by": {
        "uuid": "726f6262-6572-7440-6173-6b616e6e6121",
        "short_uuid": "3Tw1-jp9H-FjQw-8PYY",
        "name": "anna@askanna.io",
    },
    "permission": {
        "askanna.me": False,
        "askanna.admin": False,
        "askanna.member": False,
        "askanna.workspace.create": False,
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
    "modified": "2020-04-01T09:44:11.853000Z",
    "url": "http://beta.askanna.eu/3Cpy-QMzd-MVko-1rDQ/",
}


class SDKworkspaceTest(unittest.TestCase):
    def setUp(self):
        self.base_url = client.base_url

        self.responses = responses.RequestsMock()
        self.responses.start()

        self.responses.add(
            responses.POST,
            url=self.base_url + "workspace/",
            json=a_sample_workspace_response,
            match=[json_params_matcher({"name": "AskAnna", "description": "", "visibility": "PRIVATE"})],
        )
        self.responses.add(
            responses.POST,
            url=self.base_url + "workspace/",
            json=a_sample_workspace_response,
            match=[json_params_matcher({"name": "AskAnna", "description": "A description", "visibility": "PRIVATE"})],
        )
        self.responses.add(
            responses.POST,
            url=self.base_url + "workspace/",
            json=a_sample_workspace_response,
            match=[json_params_matcher({"name": "AskAnna", "description": "", "visibility": "PUBLIC"})],
        )
        self.responses.add(
            responses.GET,
            url=self.base_url + "workspace/abcd-abcd-abcd-abcd/",
            json=a_sample_workspace_response,
        )
        self.responses.add(
            responses.PATCH,
            url=self.base_url + "workspace/abcd-abcd-abcd-abcd/",
            json=a_sample_workspace_response,
            match=[json_params_matcher({"name": "new name"})],
        )
        self.responses.add(
            responses.PATCH,
            url=self.base_url + "workspace/abcd-abcd-abcd-abcd/",
            json=a_sample_workspace_response,
            match=[json_params_matcher({"description": "new description"})],
        )
        self.responses.add(
            responses.PATCH,
            url=self.base_url + "workspace/abcd-abcd-abcd-abcd/",
            json=a_sample_workspace_response,
            match=[json_params_matcher({"visibility": "PUBLIC"})],
        )
        self.responses.add(
            responses.PATCH,
            url=self.base_url + "workspace/abcd-abcd-abcd-abcd/",
            json=a_sample_workspace_response,
            match=[json_params_matcher({"name": "new name", "description": "new description"})],
        )
        self.responses.add(
            responses.PATCH,
            url=self.base_url + "workspace/abcd-abcd-abcd-abcd/",
            json=a_sample_workspace_response,
            match=[
                json_params_matcher({"name": "new name", "description": "new description", "visibility": "PUBLIC"})
            ],
        )
        self.responses.add(
            responses.DELETE,
            url=self.base_url + "workspace/abcd-abcd-abcd-abcd/",
            status=204,
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset

    def test_create_workspace_name(self):
        wgw = WorkspaceGateway()
        wgw.create(name="AskAnna")

    def test_create_workspace_description(self):
        wgw = WorkspaceGateway()
        wgw.create(name="AskAnna", description="A description")

    def test_create_workspace_no_name(self):
        wgw = WorkspaceGateway()
        with self.assertRaises(TypeError):
            wgw.create(description="A description")

    def test_create_workspace_visibility(self):
        wgw = WorkspaceGateway()
        wgw.create(name="AskAnna", visibility="PUBLIC")

    def test_create_workspace_visibility_value_error(self):
        wgw = WorkspaceGateway()
        with self.assertRaises(ValueError):
            wgw.create(name="AskAnna", visibility="public")

    def test_get_workspace(self):
        wgw = WorkspaceGateway()
        wgw.detail("abcd-abcd-abcd-abcd")

    def test_change_workspace_name(self):
        wgw = WorkspaceGateway()
        wgw.change("abcd-abcd-abcd-abcd", name="new name")

    def test_change_workspace_description(self):
        wgw = WorkspaceGateway()
        wgw.change("abcd-abcd-abcd-abcd", description="new description")

    def test_change_workspace_visibility(self):
        wgw = WorkspaceGateway()
        wgw.change("abcd-abcd-abcd-abcd", visibility="PUBLIC")

    def test_change_workspace_visibility_value_error(self):
        wgw = WorkspaceGateway()
        with self.assertRaises(ValueError):
            wgw.change("abcd-abcd-abcd-abcd", visibility="public")

    def test_change_workspace_name_description(self):
        wgw = WorkspaceGateway()
        wgw.change(
            "abcd-abcd-abcd-abcd",
            name="new name",
            description="new description",
        )

    def test_change_workspace_name_description_visibility(self):
        wgw = WorkspaceGateway()
        wgw.change("abcd-abcd-abcd-abcd", name="new name", description="new description", visibility="PUBLIC")

    def test_change_workspace_name_description_visibility_value_error(self):
        wgw = WorkspaceGateway()
        with self.assertRaises(ValueError):
            wgw.change("abcd-abcd-abcd-abcd", name="new name", description="new description", visibility="public")

    def test_change_workspace_all_empty(self):
        wgw = WorkspaceGateway()
        with self.assertRaises(SystemExit) as cm:
            wgw.change("abcd-abcd-abcd-abcd")
        self.assertEqual(cm.exception.code, 1)

    def test_delete_workspace(self):
        wgw = WorkspaceGateway()
        self.assertTrue(wgw.delete("abcd-abcd-abcd-abcd"))
