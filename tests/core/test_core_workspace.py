import unittest
import responses

from askanna.core.workspace import WorkspaceGateway

a_sample_workspace_response = {
    "uuid": "695fcc8b-ba8c-4575-a1e0-f0fcfc70a349",
    "created": "2020-04-01T09:44:11.853000Z",
    "modified": "2020-04-01T09:44:11.853000Z",
    "name": "AskAnna",
    "description": "",
    "short_uuid": "3Cpy-QMzd-MVko-1rDQ",
}


class SDKworkspaceTest(unittest.TestCase):
    def setUp(self):
        self.responses = responses.RequestsMock()
        self.responses.start()

        self.responses.add(
            responses.PATCH,
            url="https://beta-api.askanna.eu/v1/workspace/abcd-abcd-abcd-abcd/",
            json=a_sample_workspace_response,
            match=[responses.json_params_matcher({"name": "new name"})],
        )

        self.responses.add(
            responses.PATCH,
            url="https://beta-api.askanna.eu/v1/workspace/abcd-abcd-abcd-abcd/",
            json=a_sample_workspace_response,
            match=[responses.json_params_matcher({"description": "new description"})],
        )
        self.responses.add(
            responses.PATCH,
            url="https://beta-api.askanna.eu/v1/workspace/abcd-abcd-abcd-abcd/",
            json=a_sample_workspace_response,
            match=[
                responses.json_params_matcher(
                    {"name": "new name", "description": "new description"}
                )
            ],
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset

    def test_change_workspace_name(self):
        wgw = WorkspaceGateway()
        wgw.change("abcd-abcd-abcd-abcd", name="new name")

    def test_change_workspace_description(self):
        wgw = WorkspaceGateway()
        wgw.change("abcd-abcd-abcd-abcd", description="new description")

    def test_change_workspace_name_description(self):
        wgw = WorkspaceGateway()
        wgw.change(
            "abcd-abcd-abcd-abcd",
            name="new name",
            description="new description",
        )

    def test_change_workspace_all_empty(self):
        wgw = WorkspaceGateway()
        with self.assertRaises(SystemExit) as cm:
            wgw.change("abcd-abcd-abcd-abcd")
        self.assertEqual(cm.exception.code, 1)
