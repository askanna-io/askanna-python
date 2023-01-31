import unittest

import responses

from askanna.gateways.api_client import client
from askanna.gateways.job import JobGateway

a_sample_run_response = {
    "suuid": "4F8q-nTCK-M2nA-aXUg",
    "status": "queued",
    "name": "Run with name",
    "next_url": "https://beta-api.askanna.eu/v1/run/4F8q-nTCK-M2nA-aXUg/status/",
    "started": None,
    "finished": None,
    "duration": 0,
    "created_by": {
        "relation": "membership",
        "suuid": "4bWd-sWHg-Xz4o-8ICi",
        "name": "Robbert",
        "job_title": "Founder AskAnna",
        "role": {"name": "Workspace Admin", "code": "WA"},
        "status": "active",
    },
    "job": {
        "relation": "jobdef",
        "suuid": "43hH-OthG-zG6G-9OVK",
        "name": "test-payload",
    },
    "project": {
        "relation": "project",
        "suuid": "7MQT-6309-9g3t-R5QR",
        "name": "AskAnna Sandbox",
    },
    "workspace": {
        "relation": "workspace",
        "suuid": "3Cpy-QMzd-MVko-1rDQ",
        "name": "AskAnna",
    },
    "created": "2021-04-22T10:31:29.249069Z",
    "modified": "2021-04-22T10:31:29.249091Z",
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
            status=201,
        )

        self.responses.add(
            responses.POST,
            url=self.base_url + "job/abcd-abcd-abcd-abcd/run/request/batch/?name=new+name",
            json=a_sample_run_response,
            status=201,
        )

        self.responses.add(
            responses.POST,
            url=self.base_url + "job/abcd-abcd-abcd-abcd/run/request/batch/?description=new+description",
            json=a_sample_run_response,
            status=201,
        )
        self.responses.add(
            responses.POST,
            url=self.base_url + "job/abcd-abcd-abcd-abcd/run/request/batch/?name=new+name&description=new+description",
            json=a_sample_run_response,
            status=201,
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
