import os
import shutil
import tempfile
import unittest

import pytest
import responses

from askanna import result as askanna_result
from askanna.core import exceptions
from askanna.core.apiclient import client
from tests.create_fake_files import create_json_file


class TestSDKResult(unittest.TestCase):
    def setUp(self):
        self.environ_bck = dict(os.environ)
        os.environ["AA_REMOTE"] = "https://beta-api.askanna.eu"
        os.environ["AA_TOKEN"] = "12345678910"  # nosec

        self.tempdir = tempfile.mkdtemp(prefix="askanna-test-cli-result")
        self.result_json_file = create_json_file(self.tempdir, 10)

        with open(self.result_json_file, "rb") as f:
            self.content = f.read()

        self.base_url = client.base_url
        self.responses = responses.RequestsMock()
        self.responses.start()
        self.responses.add(
            responses.HEAD,
            url=self.base_url + "result/abcd-abcd-abcd-abcd/",
            headers={"Content-Length": str(os.path.getsize(self.result_json_file)), "Accept-Ranges": "bytes"},
            content_type="application/json",
            status=200,
        )
        self.responses.add(
            responses.HEAD,
            url=self.base_url + "result/1234-1234-1234-1234/",
            status=404,
        )
        self.responses.add(
            responses.GET,
            url=self.base_url + "result/abcd-abcd-abcd-abcd/",
            headers={"Content-Length": str(os.path.getsize(self.result_json_file)), "Accept-Ranges": "bytes"},
            content_type="application/json",
            status=200,
            body=self.content,
        )
        self.responses.add(
            responses.GET,
            url=self.base_url + "result/1234-1234-1234-1234/",
            status=404,
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset

        os.remove(self.result_json_file)
        shutil.rmtree(self.tempdir, ignore_errors=True)

        os.environ.clear()
        os.environ.update(self.environ_bck)

    def test_result_get(self):
        self.assertEqual(askanna_result.get("abcd-abcd-abcd-abcd"), self.content)

    def test_result_get_does_not_exist(self):
        with pytest.raises(exceptions.GetError):
            askanna_result.get("1234-1234-1234-1234")

    def test_result_get_content_type(self):
        self.assertEqual(askanna_result.get_content_type("abcd-abcd-abcd-abcd"), "application/json")

    def test_result_get_content_type_does_not_exist(self):
        with pytest.raises(exceptions.HeadError):
            askanna_result.get_content_type("1234-1234-1234-1234")
