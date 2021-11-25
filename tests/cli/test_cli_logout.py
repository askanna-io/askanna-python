from click.testing import CliRunner
from faker import Faker
from faker.providers import date_time, internet, file, misc
import os
import shutil
import tempfile
import unittest

from askanna.cli.tool import cli_commands
from askanna.config import config


fake = Faker()
fake.add_provider(date_time)
fake.add_provider(internet)
fake.add_provider(misc)
fake.add_provider(file)


class TestCliLogin(unittest.TestCase):
    """
    askanna login

    We expect to be able to setup authentication using arguments or via a prompt
    """

    def setUp(self):
        self.environ_bck = dict(os.environ)
        self.tempdir = tempfile.mkdtemp(prefix='askanna-test-cli-login')

        self.remote_url = 'https://' + fake.hostname()
        self.email = fake.email()
        self.password = fake.password(length=12)
        self.token_value = fake.password(length=40)

        config.server.server_config_path = self.tempdir + '/.askanna.yml'
        config.server.remote = self.remote_url
        config.server.token = self.token_value

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.environ_bck)

        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_command_logout_base(self):
        result = CliRunner().invoke(cli_commands, "logout --help")

        assert not result.exception
        assert result.exit_code == 0
        assert "logout" in result.output
        assert "token" in result.output

    def test_command_logout(self):
        assert config.server.token == self.token_value

        result = CliRunner().invoke(cli_commands, "logout")

        assert not result.exception
        assert result.exit_code == 0
        assert "You have been logged out" in result.output
        assert config.server.token == ''
