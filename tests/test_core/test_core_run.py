import unittest

import responses

from askanna.gateways.api_client import client
from askanna.gateways.job import JobGateway

a_sample_run_response = {
    "message_type": "status",
    "status": "queued",
    "uuid": "8b73cb55-1ea3-49e1-a294-590a16b60f3f",
    "short_uuid": "4F8q-nTCK-M2nA-aXUg",
    "name": "Run with name",
    "created": "2021-04-22T10:31:29.249069Z",
    "updated": "2021-04-22T10:31:29.249091Z",
    "finished": None,
    "job": {
        "relation": "jobdef",
        "name": "test-payload",
        "uuid": "85632085-5a62-4cf3-9142-34237f5f32d1",
        "short_uuid": "43hH-OthG-zG6G-9OVK",
    },
    "project": {
        "relation": "project",
        "name": "AskAnna Sandbox",
        "uuid": "f1e2144a-87f9-4936-8562-4304c51332ea",
        "short_uuid": "7MQT-6309-9g3t-R5QR",
    },
    "workspace": {
        "relation": "workspace",
        "name": "AskAnna",
        "uuid": "695fcc8b-ba8c-4575-a1e0-f0fcfc70a349",
        "short_uuid": "3Cpy-QMzd-MVko-1rDQ",
    },
    "next_url": "https://beta-api.askanna.eu/v1/status/4F8q-nTCK-M2nA-aXUg/",
}


class SDKRunTest(unittest.TestCase):
    def setUp(self):
        self.base_url = client.askanna_url.base_url

        self.responses = responses.RequestsMock()
        self.responses.start()

        self.responses.add(
            responses.POST,
            url=self.base_url + "job/abcd-abcd-abcd-abcd/run/request/batch/",
            json=a_sample_run_response,
        )

        self.responses.add(
            responses.POST,
            url=self.base_url + "job/abcd-abcd-abcd-abcd/run/request/batch/?name=new+name",
            json=a_sample_run_response,
        )

        self.responses.add(
            responses.POST,
            url=self.base_url + "job/abcd-abcd-abcd-abcd/run/request/batch/?description=new+description",
            json=a_sample_run_response,
        )
        self.responses.add(
            responses.POST,
            url=self.base_url + "job/abcd-abcd-abcd-abcd/run/request/batch/?name=new+name&description=new+description",
            json=a_sample_run_response,
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset

    def test_run_with_name(self):
        jgw = JobGateway()
        jgw.run_request("abcd-abcd-abcd-abcd", name="new name")

    def test_run_with_description(self):
        jgw = JobGateway()
        jgw.run_request("abcd-abcd-abcd-abcd", description="new description")

    def test_run_with_name_and_description(self):
        jgw = JobGateway()
        jgw.run_request(
            "abcd-abcd-abcd-abcd",
            name="new name",
            description="new description",
        )

    def test_run_default(self):
        jgw = JobGateway()
        jgw.run_request("abcd-abcd-abcd-abcd")
