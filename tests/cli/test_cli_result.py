from click.testing import CliRunner
import os
import responses
import shutil
import tempfile
import unittest

from askanna.cli.tool import cli_commands
from askanna.core import client
from tests.create_fake_files import create_json_file


class TestCLIResult(unittest.TestCase):
    """
    askanna result

    We expect to be able to get result from a run
    """

    def setUp(self):
        self.environ_bck = dict(os.environ)
        os.environ["AA_REMOTE"] = "https://beta-api.askanna.eu/v1/"
        os.environ["AA_TOKEN"] = "12345678910"

        self.tempdir = tempfile.mkdtemp(prefix="askanna-test-cli-result")
        self.result_json_file = create_json_file(self.tempdir, 10)

        with open(self.result_json_file, "rb") as f:
            content = f.read()

        self.base_url = client.config.remote
        self.responses = responses.RequestsMock()
        self.responses.start()
        self.responses.add(
            responses.HEAD,
            url=self.base_url + "result/abcd-abcd-abcd-abcd/",
            headers={'Content-Length': str(os.path.getsize(self.result_json_file)), 'Accept-Ranges': 'bytes'},
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
            headers={"Range": f"bytes=0-{os.path.getsize(self.result_json_file)}"},
            stream=True,
            content_type="application/json",
            status=206,
            body=content
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset

        os.remove(self.result_json_file)
        shutil.rmtree(self.tempdir, ignore_errors=True)

        os.environ.clear()
        os.environ.update(self.environ_bck)

    def test_command_result_base(self):
        result = CliRunner().invoke(cli_commands, "result --help")

        assert not result.exception
        assert "result" in result.output
        assert "noop" not in result.output

    def test_command_result_get(self):
        result = CliRunner().invoke(cli_commands, "result get --help")

        assert "result" in result.output
        assert "get [OPTIONS]" in result.output
        assert "noop" not in result.output

    def test_command_result_get_prompt_invalid_suuid(self):
        result = CliRunner().invoke(cli_commands, "result get", input="test")

        assert result.exception
        assert "Run SUUID: test" in result.output

    def test_command_result_get_unknown_file(self):
        result = CliRunner().invoke(cli_commands, "result get", input="1234-1234-1234-1234")

        assert result.exception
        assert "Run SUUID: 1234-1234-1234-1234" in result.output
        assert "404 - We cannot find this result for you" in result.output

    def test_command_result_get_prompt(self):
        result = CliRunner().invoke(cli_commands, "result get", input="abcd-abcd-abcd-abcd")
        os.remove("result_abcd-abcd-abcd-abcd.json")

        assert not result.exception
        assert "Run SUUID: abcd-abcd-abcd-abcd" in result.output
        assert "Downloading the result has started..." in result.output
        assert "The result is saved in: result_abcd-abcd-abcd-abcd.json" in result.output

    def test_command_result_get_already_exist(self):
        CliRunner().invoke(cli_commands, "result get", input="abcd-abcd-abcd-abcd")
        result = CliRunner().invoke(cli_commands, "result get", input="abcd-abcd-abcd-abcd")
        os.remove("result_abcd-abcd-abcd-abcd.json")

        assert result.exception
        assert "Run SUUID: abcd-abcd-abcd-abcd" in result.output
        assert "The output file already exists. We will not overwrite the existing file." in result.output

    def test_command_result_get_argument_full(self):
        result = CliRunner().invoke(cli_commands, "result get --id abcd-abcd-abcd-abcd")
        os.remove("result_abcd-abcd-abcd-abcd.json")

        assert not result.exception
        assert "Downloading the result has started..." in result.output
        assert "The result is saved in: result_abcd-abcd-abcd-abcd.json" in result.output

    def test_command_result_get_argument_short(self):
        result = CliRunner().invoke(cli_commands, "result get -i abcd-abcd-abcd-abcd")
        os.remove("result_abcd-abcd-abcd-abcd.json")

        assert not result.exception
        assert "Downloading the result has started..." in result.output
        assert "The result is saved in: result_abcd-abcd-abcd-abcd.json" in result.output

    def test_command_result_get_argument_output_dir(self):
        result = CliRunner().invoke(cli_commands, f"result get --id abcd-abcd-abcd-abcd --output {self.tempdir}")

        assert result.exception
        assert "The output argument is a directory. Please provide a file name for the output." in result.output

    def test_command_result_get_argument_output_file(self):
        output_file = self.tempdir + "/result-json-abcd-abcd-abcd-abcd.json"
        result = CliRunner().invoke(cli_commands, f"result get --id abcd-abcd-abcd-abcd --output {output_file}")

        self.assertEqual(os.path.getsize(self.result_json_file), os.path.getsize(output_file))
        os.remove(output_file)

        assert not result.exception
        assert "Downloading the result has started..." in result.output
        assert f"The result is saved in: {output_file}" in result.output

    def test_command_result_get_argument_output_file_short(self):
        output_file = self.tempdir + "/result-json-abcd-abcd-abcd-abcd.json"
        result = CliRunner().invoke(cli_commands, f"result get --id abcd-abcd-abcd-abcd -o {output_file}")

        self.assertEqual(os.path.getsize(self.result_json_file), os.path.getsize(output_file))
        os.remove(output_file)

        assert not result.exception
        assert "Downloading the result has started..." in result.output
        assert f"The result is saved in: {output_file}" in result.output
