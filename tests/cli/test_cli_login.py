from click.testing import CliRunner
from faker import Faker
from faker.providers import date_time, internet, file, misc
import os
import responses
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
        config.server.token = ''

        self.responses = responses.RequestsMock()
        self.responses.start()
        self.responses.add(
            responses.POST,
            url=self.remote_url + '/rest-auth/login/',
            status=200,
            json={'key': self.token_value},
        )
        self.responses.add(
            responses.GET,
            url=self.remote_url + '/rest-auth/user/',
            status=200,
            json={
                'name': fake.name(),
                'email': self.email,
                'short_uuid': fake.uuid4(),
                'is_active': True,
                'date_joined': fake.iso8601(),
                'last_login': fake.iso8601()
            },
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset

        os.environ.clear()
        os.environ.update(self.environ_bck)

        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_command_login_base(self):
        result = CliRunner().invoke(cli_commands, "login --help")

        assert not result.exception
        assert result.exit_code == 0
        assert "login" in result.output
        assert "remote" in result.output
        assert "email" in result.output
        assert "password" in result.output
        assert "noop" not in result.output

    def test_command_login(self):
        result = CliRunner().invoke(
            cli_commands,
            f"login --email {self.email} --password {self.password} --remote {self.remote_url}"
        )

        assert not result.exception
        assert result.exit_code == 0
        assert self.email in result.output
        assert self.password not in result.output
        assert self.token_value not in result.output

    def test_command_login_double(self):
        CliRunner().invoke(
            cli_commands,
            f"login --email {self.email} --password {self.password} --remote {self.remote_url}"
        )
        result = CliRunner().invoke(
            cli_commands,
            f"login --email {self.email} --password {self.password} --remote {self.remote_url}"
        )

        assert not result.exception
        assert result.exit_code == 0
        assert "already logged in" in result.output
        assert self.email in result.output
        assert "askanna logout" in result.output
        assert self.password not in result.output
        assert self.token_value not in result.output

    def test_command_ask_credentials(self):
        remote_url = 'https://' + fake.hostname()
        email = fake.email()
        password = fake.password(length=12)
        token = fake.password(length=40)

        self.responses.add(
            responses.POST,
            url=remote_url + '/rest-auth/login/',
            status=200,
            json={'key': token},
        )
        self.responses.add(
            responses.GET,
            url=remote_url + '/rest-auth/user/',
            status=200,
            json={
                'name': '',
                'email': email,
                'short_uuid': fake.uuid4(),
                'is_active': True,
                'date_joined': fake.iso8601(),
                'last_login': fake.iso8601()
            },
        )

        result = CliRunner().invoke(
            cli_commands,
            f"login --remote {remote_url}",
            input=f'{email}\n{password}'
        )

        assert "Let's login into AskAnna" in result.output
        assert "Email:" in result.output
        assert "Password:" in result.output
        assert "logged in with" in result.output

    def test_command_ask_password(self):
        remote_url = 'https://' + fake.hostname()
        email = fake.email()
        password = fake.password(length=12)
        token = fake.password(length=40)

        self.responses.add(
            responses.POST,
            url=remote_url + '/rest-auth/login/',
            status=200,
            json={'key': token},
        )
        self.responses.add(
            responses.GET,
            url=remote_url + '/rest-auth/user/',
            status=200,
            json={
                'name': '',
                'email': email,
                'short_uuid': fake.uuid4(),
                'is_active': True,
                'date_joined': fake.iso8601(),
                'last_login': fake.iso8601()
            },
        )

        result = CliRunner().invoke(
            cli_commands,
            f"login --remote {remote_url} --email {email}",
            input=f'{password}'
        )

        assert "Let's login into AskAnna" in result.output
        assert "Email:" not in result.output
        assert "Password:" in result.output
        assert "logged in with" in result.output

    def test_command_ask_email(self):
        remote_url = 'https://' + fake.hostname()
        email = fake.email()
        password = fake.password(length=12)
        token = fake.password(length=40)

        self.responses.add(
            responses.POST,
            url=remote_url + '/rest-auth/login/',
            status=200,
            json={'key': token},
        )
        self.responses.add(
            responses.GET,
            url=remote_url + '/rest-auth/user/',
            status=200,
            json={
                'name': '',
                'email': email,
                'short_uuid': fake.uuid4(),
                'is_active': True,
                'date_joined': fake.iso8601(),
                'last_login': fake.iso8601()
            },
        )

        result = CliRunner().invoke(
            cli_commands,
            f"login --remote {remote_url} --password {password}",
            input=f'{email}'
        )

        assert "Let's login into AskAnna" in result.output
        assert "Email:" in result.output
        assert "Password:" not in result.output
        assert "logged in with" in result.output
