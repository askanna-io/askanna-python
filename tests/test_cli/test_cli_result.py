import os
import shutil
import tempfile
import unittest

import responses
from click.testing import CliRunner
from responses import matchers

from askanna.cli import cli
from askanna.config import config
from tests.create_fake_files import create_json_file


class TestCLIResult(unittest.TestCase):
    """
    askanna result

    We expect to be able to get result from a run
    """

    def setUp(self):
        self.environ_bck = dict(os.environ)
        self.base_url = "https://beta-api.askanna.eu/v1/run/"
        config.server.remote = "https://beta-api.askanna.eu"
        config.server.token = "12345678910"  # nosec: B105

        self.tempdir = tempfile.mkdtemp(prefix="askanna-test-cli-result")
        self.result_json_file = create_json_file(self.tempdir, 10)

        with open(self.result_json_file, "rb") as f:
            content = f.read()

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
                "started": "2022-10-31T11:57:09.142053Z",
                "finished": "2022-10-31T11:57:38.780094Z",
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
                    "suuid": "1S6G-K3fI-visU-LKac",
                    "relation": "workspace",
                    "name": "Demo AskAnna",
                },
                "created": "2022-10-31T11:57:08.646054Z",
                "modified": "2022-10-31T11:57:38.804488Z",
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
                "started": "2022-10-31T11:57:09.142053Z",
                "finished": "2022-10-31T11:57:38.780094Z",
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
                "created": "2022-10-31T11:57:08.646054Z",
                "modified": "2022-10-31T11:57:38.804488Z",
            },
        )
        self.responses.add(
            responses.HEAD,
            url=self.base_url + "1234-1234-1234-1234/result/",
            status=404,
        )
        self.responses.add(
            responses.GET,
            url=self.base_url + "abcd-abcd-abcd-abcd/result/",
            headers={"Range": f"bytes=0-{os.path.getsize(self.result_json_file)}"},
            match=[matchers.request_kwargs_matcher({"stream": True})],
            content_type="application/json",
            status=206,
            body=content,
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset

        os.remove(self.result_json_file)
        shutil.rmtree(self.tempdir, ignore_errors=True)

        os.environ.clear()
        os.environ.update(self.environ_bck)

    def test_command_result_base(self):
        result = CliRunner().invoke(cli, "result --help")

        assert not result.exception
        assert "result" in result.output
        assert "noop" not in result.output

    def test_command_result_get(self):
        result = CliRunner().invoke(cli, "result get --help")

        assert "result" in result.output
        assert "get [OPTIONS]" in result.output
        assert "noop" not in result.output

    def test_command_result_get_prompt_invalid_suuid(self):
        result = CliRunner().invoke(cli, "result get", input="test")

        assert result.exception
        assert "Run SUUID: test" in result.output

    def test_command_result_get_unknown_file(self):
        result = CliRunner().invoke(cli, "result get", input="1234-1234-1234-1234")

        assert result.exception
        assert "Run SUUID: 1234-1234-1234-1234" in result.output
        assert "404 - The result for run SUUID '1234-1234-1234-1234' was not found" in result.output

    def test_command_result_get_prompt(self):
        result = CliRunner().invoke(cli, "result get", input="abcd-abcd-abcd-abcd")
        os.remove("result_abcd-abcd-abcd-abcd_filename.json")

        assert not result.exception
        assert "Run SUUID: abcd-abcd-abcd-abcd" in result.output
        assert "Downloading the result has started..." in result.output
        assert "The result is saved in: result_abcd-abcd-abcd-abcd_filename.json" in result.output

    def test_command_result_get_already_exist(self):
        CliRunner().invoke(cli, "result get", input="abcd-abcd-abcd-abcd")
        result = CliRunner().invoke(cli, "result get", input="abcd-abcd-abcd-abcd")
        os.remove("result_abcd-abcd-abcd-abcd_filename.json")

        assert result.exception
        assert "Run SUUID: abcd-abcd-abcd-abcd" in result.output
        assert (
            "The file 'result_abcd-abcd-abcd-abcd_filename.json' already exists. "
            "We will not overwrite the existing file." in result.output
        )

    def test_command_result_get_argument_full(self):
        result = CliRunner().invoke(cli, "result get --id abcd-abcd-abcd-abcd")
        os.remove("result_abcd-abcd-abcd-abcd_filename.json")

        assert not result.exception
        assert "Downloading the result has started..." in result.output
        assert "The result is saved in: result_abcd-abcd-abcd-abcd_filename.json" in result.output

    def test_command_result_get_argument_short(self):
        result = CliRunner().invoke(cli, "result get -i abcd-abcd-abcd-abcd")
        os.remove("result_abcd-abcd-abcd-abcd_filename.json")

        assert not result.exception
        assert "Downloading the result has started..." in result.output
        assert "The result is saved in: result_abcd-abcd-abcd-abcd_filename.json" in result.output

    def test_command_result_get_argument_output_dir(self):
        result = CliRunner().invoke(cli, f"result get --id abcd-abcd-abcd-abcd --output {self.tempdir}")

        assert result.exception
        assert "The output argument is a directory. Please provide a filename for the output." in result.output

    def test_command_result_get_argument_output_file(self):
        output_file = self.tempdir + "/result-json-abcd-abcd-abcd-abcd.json"
        result = CliRunner().invoke(cli, f"result get --id abcd-abcd-abcd-abcd --output {output_file}")

        self.assertEqual(os.path.getsize(self.result_json_file), os.path.getsize(output_file))
        os.remove(output_file)

        assert not result.exception
        assert "Downloading the result has started..." in result.output
        assert f"The result is saved in: {output_file}" in result.output

    def test_command_result_get_argument_output_file_short(self):
        output_file = self.tempdir + "/result-json-abcd-abcd-abcd-abcd.json"
        result = CliRunner().invoke(cli, f"result get --id abcd-abcd-abcd-abcd -o {output_file}")

        self.assertEqual(os.path.getsize(self.result_json_file), os.path.getsize(output_file))
        os.remove(output_file)

        assert not result.exception
        assert "Downloading the result has started..." in result.output
        assert f"The result is saved in: {output_file}" in result.output
