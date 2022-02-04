import os
import shutil
import tempfile
import unittest

import responses
from click.testing import CliRunner

from askanna.cli.tool import cli_commands
from askanna.core.apiclient import client
from tests.create_fake_files import create_zip_file


class TestCLIArtifact(unittest.TestCase):
    """
    askanna artifact

    We expect to be able to get artifact from a run
    """

    def setUp(self):
        self.environ_bck = dict(os.environ)
        os.environ["AA_REMOTE"] = "https://beta-api.askanna.eu"
        os.environ["AA_TOKEN"] = "12345678910"  # nosec

        self.tempdir = tempfile.mkdtemp(prefix="askanna-test-cli-artifact")
        self.artifact_zip_file = create_zip_file(self.tempdir, 10)

        with open(self.artifact_zip_file, "rb") as f:
            content = f.read()

        self.base_url = client.base_url
        url_download_file = "https://cdn-beta-api.askanna.eu/files/artifacts/65deef6cc430ab83b451e659ba4562cf/476120827b1e224d747c6e444961c9e6/afdf82c9a39161d6041d785bcbd8f0e4/artifact_2abeb6346f5a679078379d500043e41d.zip"  # noqa

        self.responses = responses.RequestsMock()
        self.responses.start()
        self.responses.add(
            responses.HEAD,
            url=self.base_url + "artifact/abcd-abcd-abcd-abcd/",
            headers={"Location": f"{url_download_file}"},
            status=302,
        )
        self.responses.add(
            responses.HEAD,
            url=self.base_url + "artifact/1234-1234-1234-1234/",
            status=404,
        )
        self.responses.add(
            responses.HEAD,
            url=url_download_file,
            headers={"Content-Length": str(os.path.getsize(self.artifact_zip_file)), "Accept-Ranges": "bytes"},
            content_type="application/zip",
            status=200,
        )
        self.responses.add(
            responses.GET,
            url=url_download_file,
            headers={"Range": f"bytes=0-{os.path.getsize(self.artifact_zip_file)}"},
            stream=True,
            content_type="application/zip",
            status=206,
            body=content,
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset

        os.remove(self.artifact_zip_file)
        shutil.rmtree(self.tempdir, ignore_errors=True)

        os.environ.clear()
        os.environ.update(self.environ_bck)

    def test_command_artifact_base(self):
        result = CliRunner().invoke(cli_commands, "artifact --help")

        assert not result.exception
        assert "artifact" in result.output
        assert "noop" not in result.output

    def test_command_artifact_get(self):
        result = CliRunner().invoke(cli_commands, "artifact get --help")

        assert "artifact" in result.output
        assert "get [OPTIONS]" in result.output
        assert "noop" not in result.output

    def test_command_artifact_get_prompt_invalid_suuid(self):
        result = CliRunner().invoke(cli_commands, "artifact get", input="test")

        assert result.exception
        assert "Run SUUID: test" in result.output

    def test_command_artifact_get_unknown_file(self):
        result = CliRunner().invoke(cli_commands, "artifact get", input="1234-1234-1234-1234")

        assert result.exception
        assert "Run SUUID: 1234-1234-1234-1234" in result.output
        assert "We cannot find this artifact for you." in result.output

    def test_command_artifact_get_prompt(self):
        result = CliRunner().invoke(cli_commands, "artifact get", input="abcd-abcd-abcd-abcd")
        os.remove("artifact_abcd-abcd-abcd-abcd.zip")

        assert not result.exception
        assert "Run SUUID: abcd-abcd-abcd-abcd" in result.output
        assert "Downloading the artifact has started..." in result.output
        assert "The artifact is saved in: artifact_abcd-abcd-abcd-abcd.zip" in result.output

    def test_command_artifact_get_already_exist(self):
        CliRunner().invoke(cli_commands, "artifact get", input="abcd-abcd-abcd-abcd")
        result = CliRunner().invoke(cli_commands, "artifact get", input="abcd-abcd-abcd-abcd")
        os.remove("artifact_abcd-abcd-abcd-abcd.zip")

        assert result.exception
        assert "Run SUUID: abcd-abcd-abcd-abcd" in result.output
        assert "The output file already exists. We will not overwrite the existing file." in result.output

    def test_command_artifact_get_argument_full(self):
        result = CliRunner().invoke(cli_commands, "artifact get --id abcd-abcd-abcd-abcd")
        os.remove("artifact_abcd-abcd-abcd-abcd.zip")

        assert not result.exception
        assert "Downloading the artifact has started..." in result.output
        assert "The artifact is saved in: artifact_abcd-abcd-abcd-abcd.zip" in result.output

    def test_command_artifact_get_argument_short(self):
        result = CliRunner().invoke(cli_commands, "artifact get -i abcd-abcd-abcd-abcd")
        os.remove("artifact_abcd-abcd-abcd-abcd.zip")

        assert not result.exception
        assert "Downloading the artifact has started..." in result.output
        assert "The artifact is saved in: artifact_abcd-abcd-abcd-abcd.zip" in result.output

    def test_command_artifact_get_argument_output_dir(self):
        result = CliRunner().invoke(cli_commands, f"artifact get --id abcd-abcd-abcd-abcd --output {self.tempdir}")

        assert result.exception
        assert "The output argument is a directory. Please provide a file name (zip) for the output." in result.output

    def test_command_artifact_get_argument_output_file(self):
        output_file = self.tempdir + "/artifact-json-abcd-abcd-abcd-abcd.zip"
        result = CliRunner().invoke(cli_commands, f"artifact get --id abcd-abcd-abcd-abcd --output {output_file}")

        self.assertEqual(os.path.getsize(self.artifact_zip_file), os.path.getsize(output_file))
        os.remove(output_file)

        assert not result.exception
        assert "Downloading the artifact has started..." in result.output
        assert f"The artifact is saved in: {output_file}" in result.output

    def test_command_artifact_get_argument_output_file_short(self):
        output_file = self.tempdir + "/artifact-json-abcd-abcd-abcd-abcd.zip"
        result = CliRunner().invoke(cli_commands, f"artifact get --id abcd-abcd-abcd-abcd -o {output_file}")

        self.assertEqual(os.path.getsize(self.artifact_zip_file), os.path.getsize(output_file))
        os.remove(output_file)

        assert not result.exception
        assert "Downloading the artifact has started..." in result.output
        assert f"The artifact is saved in: {output_file}" in result.output
