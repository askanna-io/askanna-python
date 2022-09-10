import unittest

import responses
from responses.matchers import json_params_matcher

from askanna.core.apiclient import client
from askanna.core.project import ProjectGateway

a_sample_project_response = {
    "uuid": "f1823c3b-e9e7-47bb-a610-5462c9cd9767",
    "created_by": {
        "uuid": None,
        "short_uuid": None,
        "name": None,
    },
    "workspace": {
        "relation": "workspace",
        "name": "AskAnna",
        "uuid": "695fcc8b-ba8c-4575-a1e0-f0fcfc70a349",
        "short_uuid": "3Cpy-QMzd-MVko-1rDQ",
    },
    "package": {
        "uuid": "3b499701-8713-4978-9f2c-8bfe792415cb",
        "short_uuid": "1nsB-23lb-YKp6-4HZ4",
        "name": "askanna_core.zip",
    },
    "notifications": {"all": {"email": []}, "error": {"email": []}},
    "visibility": "PUBLIC",
    "permission": {},
    "is_member": True,
    "created": "2021-01-21T10:48:11.743045Z",
    "modified": "2021-04-21T07:38:06.884762Z",
    "description": None,
    "short_uuid": "7Lif-Rhcn-IRvS-Wv7J",
    "name": "AskAnna Core",
}


class SDKProjectTest(unittest.TestCase):
    def setUp(self):
        self.base_url = client.base_url

        self.responses = responses.RequestsMock()
        self.responses.start()

        self.responses.add(
            responses.PATCH,
            url=self.base_url + "project/abcd-abcd-abcd-abcd/",
            json=a_sample_project_response,
            match=[json_params_matcher({"name": "new name"})],
        )

        self.responses.add(
            responses.PATCH,
            url=self.base_url + "project/abcd-abcd-abcd-abcd/",
            json=a_sample_project_response,
            match=[json_params_matcher({"description": "new description"})],
        )
        self.responses.add(
            responses.PATCH,
            url=self.base_url + "project/abcd-abcd-abcd-abcd/",
            json=a_sample_project_response,
            match=[json_params_matcher({"visibility": "PUBLIC"})],
        )
        self.responses.add(
            responses.PATCH,
            url=self.base_url + "project/abcd-abcd-abcd-abcd/",
            json=a_sample_project_response,
            match=[json_params_matcher({"name": "new name", "description": "new description"})],
        )
        self.responses.add(
            responses.PATCH,
            url=self.base_url + "project/abcd-abcd-abcd-abcd/",
            json=a_sample_project_response,
            match=[
                json_params_matcher({"name": "new name", "description": "new description", "visibility": "PUBLIC"})
            ],
        )
        self.responses.add(
            responses.DELETE,
            url=self.base_url + "project/abcd-abcd-abcd-abcd/",
            status=204,
        )

    def test_change_project_name(self):
        pgw = ProjectGateway()
        pgw.change("abcd-abcd-abcd-abcd", name="new name")

    def test_change_project_description(self):
        pgw = ProjectGateway()
        pgw.change("abcd-abcd-abcd-abcd", description="new description")

    def test_change_project_visibility(self):
        pgw = ProjectGateway()
        pgw.change("abcd-abcd-abcd-abcd", visibility="PUBLIC")

    def test_change_project_visibility_value_error(self):
        pgw = ProjectGateway()
        with self.assertRaises(ValueError):
            pgw.change("abcd-abcd-abcd-abcd", visibility="public")

    def test_change_project_name_description(self):
        pgw = ProjectGateway()
        pgw.change(
            "abcd-abcd-abcd-abcd",
            name="new name",
            description="new description",
        )

    def test_change_project_name_description_visibility(self):
        pgw = ProjectGateway()
        pgw.change("abcd-abcd-abcd-abcd", name="new name", description="new description", visibility="PUBLIC")

    def test_change_project_name_description_visibility_value_error(self):
        pgw = ProjectGateway()
        with self.assertRaises(ValueError):
            pgw.change("abcd-abcd-abcd-abcd", name="new name", description="new description", visibility="public")

    def test_change_project_all_empty(self):
        pgw = ProjectGateway()
        with self.assertRaises(SystemExit) as cm:
            pgw.change("abcd-abcd-abcd-abcd")
        self.assertEqual(cm.exception.code, 1)

    def test_delete_project(self):
        pgw = ProjectGateway()
        self.assertTrue(pgw.delete("abcd-abcd-abcd-abcd"))
