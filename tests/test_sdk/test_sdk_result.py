import os
import shutil
import tempfile
import unittest

import pytest
import responses

from askanna import result as askanna_result
from askanna.core import exceptions
from tests.create_fake_files import create_json_file


class TestSDKResult(unittest.TestCase):
    def setUp(self):
        self.environ_bck = dict(os.environ)
        os.environ["AA_REMOTE"] = os.getenv("AA_REMOTE", "https://beta-api.askanna.eu")
        os.environ["AA_TOKEN"] = os.getenv("AA_TOKEN", "12345678910")  # nosec

        self.tempdir = tempfile.mkdtemp(prefix="askanna-test-cli-result")
        self.result_json_file = create_json_file(self.tempdir, 10)

        with open(self.result_json_file, "rb") as f:
            self.content = f.read()

        self.base_url = "https://beta-api.askanna.eu/v1/run/"
        self.responses = responses.RequestsMock()
        self.responses.start()
        self.responses.add(
            responses.GET,
            url=self.base_url + "abcd-abcd-abcd-abcd/",
            status=200,
            json={
                "suuid": "abcd-abcd-abcd-abcd",
                "name": "",
                "description": "",
                "status": "COMPLETED",
                "started_at": "2022-10-31T11:57:09.142053Z",
                "finished_at": "2022-10-31T11:57:38.780094Z",
                "duration": 29,
                "trigger": "WEBUI",
                "created_by": {
                    "relation": "membership",
                    "suuid": "zHVi-h8lB-IU34-43g4",
                    "name": "robbert",
                    "avatar": None,
                    "job_title": "a developer",
                    "role": {"name": "Workspace Admin", "code": "WA"},
                    "status": "active",
                },
                "package": {
                    "relation": "package",
                    "suuid": "3FqG-if1Z-Gd2s-uYvq",
                    "name": "train-select-and-serve_f8cbd1bd38a544f1819b8e9b957e933c.zip",
                },
                "payload": None,
                "result": {
                    "relation": "result",
                    "suuid": "1zOZ-6Gmx-J7pL-vTRV",
                    "name": "filename.json",
                    "size": 758,
                    "extension": "pkl",
                    "mimetype": "application/octet-stream",
                },
                "artifact": None,
                "metrics_meta": {
                    "count": 3,
                    "size": 512,
                    "metric_names": [
                        {"name": "mae", "type": "float", "count": 1},
                        {"name": "r2", "type": "float", "count": 1},
                        {"name": "rmse", "type": "float", "count": 1},
                    ],
                    "label_names": [],
                },
                "variables_meta": {
                    "count": 12,
                    "size": 2950,
                    "variable_names": [
                        {"name": "model", "type": "string", "count": 1},
                        {"name": "l1_ratio", "type": "float", "count": 1},
                        {"name": "alpha", "type": "float", "count": 1},
                        {"name": "LANG", "type": "string", "count": 1},
                        {"name": "LC_ALL", "type": "string", "count": 1},
                        {"name": "TZ", "type": "string", "count": 1},
                        {"name": "AA_PACKAGE_SUUID", "type": "string", "count": 1},
                        {"name": "AA_PROJECT_SUUID", "type": "string", "count": 1},
                        {"name": "AA_JOB_NAME", "type": "string", "count": 1},
                        {"name": "AA_RUN_SUUID", "type": "string", "count": 1},
                        {"name": "AA_REMOTE", "type": "string", "count": 1},
                        {"name": "AA_TOKEN", "type": "string", "count": 1},
                    ],
                    "label_names": [
                        {"name": "source", "type": "string"},
                        {"name": "is_masked", "type": "tag"},
                        {"name": "model", "type": "tag"},
                        {"name": "parameter", "type": "tag"},
                    ],
                },
                "log": {
                    "relation": "log",
                    "suuid": "7Ais-VwmO-g7gW-d8GZ",
                    "name": "log.json",
                    "size": 13760,
                    "lines": 88,
                },
                "environment": {
                    "name": "",
                    "image": {
                        "relation": "image",
                        "suuid": "4JG8-gCre-6UgC-CTOH",
                        "name": "askanna/python:3-slim",
                        "tag": "3-slim",
                        "digest": "sha256:f4384e500febfb4e3967caa0597db99006a4f461805598c64c84c40bd14b20a9",
                    },
                    "timezone": "UTC",
                },
                "job": {
                    "relation": "jobdef",
                    "suuid": "69Nk-vIwe-0YKU-uSRB",
                    "name": "train-model",
                },
                "project": {
                    "relation": "project",
                    "suuid": "GZFT-EmyJ-CJ5V-kYKM",
                    "name": "Train, select and serve",
                },
                "workspace": {
                    "relation": "workspace",
                    "suuid": "1S6G-K3fI-visU-LKac",
                    "name": "Demo AskAnna",
                },
                "created_at": "2022-10-31T11:57:08.646054Z",
                "modified_at": "2022-10-31T11:57:38.804488Z",
            },
        )
        self.responses.add(
            responses.HEAD,
            url=self.base_url + "abcd-abcd-abcd-abcd/result/",
            headers={"Content-Length": str(os.path.getsize(self.result_json_file)), "Accept-Ranges": "bytes"},
            content_type="application/json",
            status=200,
        )
        self.responses.add(
            responses.GET,
            url=self.base_url + "1234-1234-1234-1234/",
            status=200,
            json={
                "suuid": "1234-1234-1234-1234",
                "name": "",
                "description": "",
                "status": "COMPLETED",
                "started_at": "2022-10-31T11:57:09.142053Z",
                "finished_at": "2022-10-31T11:57:38.780094Z",
                "duration": 29,
                "trigger": "WEBUI",
                "created_by": {
                    "relation": "membership",
                    "suuid": "zHVi-h8lB-IU34-43g4",
                    "name": "robbert",
                    "avatar": None,
                    "job_title": "k1",
                    "role": {"name": "Workspace Admin", "code": "WA"},
                    "status": "active",
                },
                "package": {
                    "relation": "package",
                    "suuid": "3FqG-if1Z-Gd2s-uYvq",
                    "name": "train-select-and-serve_f8cbd1bd38a544f1819b8e9b957e933c.zip",
                },
                "payload": None,
                "result": {
                    "relation": "result",
                    "suuid": "1zOZ-6Gmx-J7pL-vTRV",
                    "name": "filename.json",
                    "size": 758,
                    "extension": "pkl",
                    "mimetype": "application/octet-stream",
                },
                "artifact": None,
                "metrics_meta": {
                    "count": 3,
                    "size": 512,
                    "metric_names": [
                        {"name": "mae", "type": "float", "count": 1},
                        {"name": "r2", "type": "float", "count": 1},
                        {"name": "rmse", "type": "float", "count": 1},
                    ],
                    "label_names": [],
                },
                "variables_meta": {
                    "count": 12,
                    "size": 2950,
                    "variable_names": [
                        {"name": "model", "type": "string", "count": 1},
                        {"name": "l1_ratio", "type": "float", "count": 1},
                        {"name": "alpha", "type": "float", "count": 1},
                        {"name": "LANG", "type": "string", "count": 1},
                        {"name": "LC_ALL", "type": "string", "count": 1},
                        {"name": "TZ", "type": "string", "count": 1},
                        {"name": "AA_PACKAGE_SUUID", "type": "string", "count": 1},
                        {"name": "AA_PROJECT_SUUID", "type": "string", "count": 1},
                        {"name": "AA_JOB_NAME", "type": "string", "count": 1},
                        {"name": "AA_RUN_SUUID", "type": "string", "count": 1},
                        {"name": "AA_REMOTE", "type": "string", "count": 1},
                        {"name": "AA_TOKEN", "type": "string", "count": 1},
                    ],
                    "label_names": [
                        {"name": "source", "type": "string"},
                        {"name": "is_masked", "type": "tag"},
                        {"name": "model", "type": "tag"},
                        {"name": "parameter", "type": "tag"},
                    ],
                },
                "log": {
                    "relation": "log",
                    "suuid": "7Ais-VwmO-g7gW-d8GZ",
                    "name": "log.json",
                    "size": 13760,
                    "lines": 88,
                },
                "environment": {
                    "name": "",
                    "image": {
                        "relation": "image",
                        "suuid": "4JG8-gCre-6UgC-CTOH",
                        "name": "askanna/python:3-slim",
                        "tag": "3-slim",
                        "digest": "sha256:f4384e500febfb4e3967caa0597db99006a4f461805598c64c84c40bd14b20a9",
                    },
                    "timezone": "UTC",
                },
                "job": {
                    "relation": "jobdef",
                    "suuid": "69Nk-vIwe-0YKU-uSRB",
                    "name": "train-model",
                },
                "project": {
                    "relation": "project",
                    "suuid": "GZFT-EmyJ-CJ5V-kYKM",
                    "name": "Train, select and serve",
                },
                "workspace": {
                    "relation": "workspace",
                    "suuid": "1S6G-K3fI-visU-LKac",
                    "name": "Demo AskAnna",
                },
                "created_at": "2022-10-31T11:57:08.646054Z",
                "modified_at": "2022-10-31T11:57:38.804488Z",
            },
        )
        self.responses.add(
            responses.HEAD,
            url=self.base_url + "1234-1234-1234-1234/result/",
            status=404,
        )
        self.responses.add(
            responses.GET,
            url=self.base_url + "1234-1234-1234-1234/result/",
            status=404,
        )
        self.responses.add(
            responses.GET,
            url=self.base_url + "abcd-abcd-abcd-abcd/result/",
            content_type="application/json",
            status=200,
            body=self.content,
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
