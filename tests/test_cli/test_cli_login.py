import os
import shutil
import tempfile
import unittest

import responses
from click.testing import CliRunner
from faker import Faker
from faker.providers import date_time, file, internet, misc

from askanna.cli import cli
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
        self.tempdir = tempfile.mkdtemp(prefix="askanna-test-cli-login")

        self.ui_url = "https://" + fake.hostname()
        self.ui_url_with_slash = self.ui_url + "/"
        self.wrong_config_url = "https://" + fake.hostname()
        self.remote_url = "https://" + fake.hostname()
        self.email = fake.email()
        self.password = fake.password(length=12)
        self.token_value = fake.password(length=40)

        config.server.server_config_path = self.tempdir + "/.askanna.yml"
        config.server.remote = self.remote_url
        config.server.token = ""  # nosec B105

        self.responses = responses.RequestsMock()
        self.responses.start()
        self.responses.add(
            responses.POST,
            url=self.remote_url + "/v1/auth/login/",
            status=200,
            json={"key": self.token_value},
        )
        self.responses.add(
            responses.GET,
            url=self.remote_url + "/v1/auth/user/",
            status=200,
            json={
                "name": fake.name(),
                "email": self.email,
                "suuid": fake.uuid4(),
                "is_active": True,
                "date_joined": fake.iso8601(),
                "last_login": fake.iso8601(),
            },
        )
        self.responses.add(
            responses.GET,
            url=f"{self.ui_url}/askanna-config.yml",
            content_type="application/octet-stream",
            status=200,
            body=f"askanna-remote: {self.remote_url}\n",
        )
        self.responses.add(
            responses.GET,
            url=f"{self.wrong_config_url}/askanna-config.yml",
            content_type="application/octet-stream",
            status=200,
            body=f"no-remote: {self.remote_url}\n",
        )
        self.responses.add(
            responses.POST,
            url="https://beta-api.askanna.eu/v1/auth/login/",
            status=200,
            json={"key": self.token_value},
        )
        self.responses.add(
            responses.GET,
            url="https://beta-api.askanna.eu/v1/auth/user/",
            status=200,
            json={
                "name": fake.name(),
                "email": self.email,
                "suuid": fake.uuid4(),
                "is_active": True,
                "date_joined": fake.iso8601(),
                "last_login": fake.iso8601(),
            },
        )

    def tearDown(self):
        self.responses.stop
        self.responses.reset

        os.environ.clear()
        os.environ.update(self.environ_bck)

        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_command_login_base(self):
        result = CliRunner().invoke(cli, "login --help")

        assert not result.exception
        assert result.exit_code == 0
        assert "login" in result.output
        assert "email" in result.output
        assert "password" in result.output
        assert "url" in result.output
        assert "remote" in result.output
        assert "noop" not in result.output

    def test_command_login_url(self):
        result = CliRunner().invoke(cli, f"login --email {self.email} --password {self.password} --url {self.ui_url}")

        assert not result.exception
        assert result.exit_code == 0
        assert self.email in result.output
        assert self.password not in result.output
        assert self.token_value not in result.output

    def test_command_login_set_beta_ui_url(self):
        result = CliRunner().invoke(
            cli, f"login --email {self.email} --password {self.password} --remote https://beta-api.askanna.eu"
        )

        assert not result.exception
        assert result.exit_code == 0
        assert self.email in result.output
        assert self.password not in result.output
        assert self.token_value not in result.output
        assert "https://beta.askanna.eu" in config.server.ui

    def test_command_login_url_with_slash(self):
        result = CliRunner().invoke(
            cli, f"login --email {self.email} --password {self.password} --url {self.ui_url_with_slash}"
        )

        assert not result.exception
        assert result.exit_code == 0
        assert self.email in result.output
        assert self.password not in result.output
        assert self.token_value not in result.output

    def test_command_login_url_wrong_config(self):
        result = CliRunner().invoke(
            cli, f"login --email {self.email} --password {self.password} --url {self.wrong_config_url}"
        )

        assert result.exception
        assert result.exit_code == 1
        assert self.password not in result.output
        assert self.token_value not in result.output

    def test_command_login_remote(self):
        result = CliRunner().invoke(
            cli, f"login --email {self.email} --password {self.password} --remote {self.remote_url}"
        )

        assert not result.exception
        assert result.exit_code == 0
        assert self.email in result.output
        assert self.password not in result.output
        assert self.token_value not in result.output
        assert f"You are logged in with email '{self.email}'" in result.output

    def test_command_login_remote_with_slash(self):
        remote_with_slash = self.remote_url + "/"
        result = CliRunner().invoke(
            cli, f"login --email {self.email} --password {self.password} --remote {remote_with_slash}"
        )

        assert not result.exception
        assert result.exit_code == 0
        assert self.email in result.output
        assert self.password not in result.output
        assert self.token_value not in result.output
        assert f"You are logged in with email '{self.email}'" in result.output

    def test_command_login_remote_with_v1(self):
        remote_with_v1 = self.remote_url + "/v1/"
        result = CliRunner().invoke(
            cli, f"login --email {self.email} --password {self.password} --remote {remote_with_v1}"
        )

        assert not result.exception
        assert result.exit_code == 0
        assert self.email in result.output
        assert self.password not in result.output
        assert self.token_value not in result.output
        assert f"You are logged in with email '{self.email}'" in result.output

    def test_command_login_remote_with_v1_part_2(self):
        remote_with_v1 = self.remote_url + "/v1"
        result = CliRunner().invoke(
            cli, f"login --email {self.email} --password {self.password} --remote {remote_with_v1}"
        )

        assert not result.exception
        assert result.exit_code == 0
        assert self.email in result.output
        assert self.password not in result.output
        assert self.token_value not in result.output
        assert f"You are logged in with email '{self.email}'" in result.output

    def test_command_login_url_and_remote(self):
        result = CliRunner().invoke(
            cli,
            f"login --email {self.email} --password {self.password} --url {self.ui_url} --remote {self.remote_url}",
        )

        assert not result.exception
        assert result.exit_code == 0
        assert self.email in result.output
        assert self.password not in result.output
        assert self.token_value not in result.output

    def test_command_login_url_and_different_remote(self):
        different_remote = "https://" + fake.hostname()
        result = CliRunner().invoke(
            cli,
            f"login --email {self.email} --password {self.password} --url {self.ui_url} --remote {different_remote}",
        )

        assert result.exception
        assert result.exit_code == 1
        assert self.password not in result.output
        assert self.token_value not in result.output

    def test_command_login_double_login_again(self):
        CliRunner().invoke(cli, f"login --email {self.email} --password {self.password} --remote {self.remote_url}")
        result = CliRunner().invoke(
            cli,
            f"login --email {self.email} --password {self.password} --remote {self.remote_url}",
            input="y",
        )

        assert not result.exception
        assert result.exit_code == 0
        assert "You are already logged in with email" in result.output
        assert self.email in result.output
        assert "Do you want to log out email" in result.output
        assert self.password not in result.output
        assert self.token_value not in result.output
        assert "Login with a new account aborted." not in result.output
        assert f"You are logged in with email '{self.email}'" in result.output

    def test_command_login_double_abort(self):
        CliRunner().invoke(cli, f"login --email {self.email} --password {self.password} --remote {self.remote_url}")
        result = CliRunner().invoke(
            cli,
            f"login --email {self.email} --password {self.password} --remote {self.remote_url}",
            input="n",
        )

        assert not result.exception
        assert result.exit_code == 0
        assert f"You are already logged in with email '{self.email}'." in result.output
        assert self.email in result.output
        assert "Do you want to log out email" in result.output
        assert self.password not in result.output
        assert self.token_value not in result.output
        assert "Login with a new account aborted." in result.output
        assert f"You are logged in with email '{self.email}'" not in result.output

    def test_command_ask_credentials(self):
        remote_url = "https://" + fake.hostname()
        email = fake.email()
        password = fake.password(length=12)
        token = fake.password(length=40)

        self.responses.add(
            responses.POST,
            url=remote_url + "/v1/auth/login/",
            status=200,
            json={"key": token},
        )
        self.responses.add(
            responses.GET,
            url=remote_url + "/v1/auth/user/",
            status=200,
            json={
                "name": "",
                "email": email,
                "suuid": fake.uuid4(),
                "is_active": True,
                "date_joined": fake.iso8601(),
                "last_login": fake.iso8601(),
            },
        )

        result = CliRunner().invoke(cli, f"login --remote {remote_url}", input=f"{email}\n{password}")

        assert "Let's login into AskAnna" in result.output
        assert "Email:" in result.output
        assert "Password:" in result.output
        assert "logged in with" in result.output

    def test_command_ask_password(self):
        remote_url = "https://" + fake.hostname()
        email = fake.email()
        password = fake.password(length=12)
        token = fake.password(length=40)

        self.responses.add(
            responses.POST,
            url=remote_url + "/v1/auth/login/",
            status=200,
            json={"key": token},
        )
        self.responses.add(
            responses.GET,
            url=remote_url + "/v1/auth/user/",
            status=200,
            json={
                "name": "",
                "email": email,
                "suuid": fake.uuid4(),
                "is_active": True,
                "date_joined": fake.iso8601(),
                "last_login": fake.iso8601(),
            },
        )

        result = CliRunner().invoke(cli, f"login --remote {remote_url} --email {email}", input=f"{password}")

        assert "Let's login into AskAnna" in result.output
        assert "Email:" not in result.output
        assert "Password:" in result.output
        assert "logged in with" in result.output

    def test_command_ask_email(self):
        remote_url = "https://" + fake.hostname()
        email = fake.email()
        password = fake.password(length=12)
        token = fake.password(length=40)

        self.responses.add(
            responses.POST,
            url=remote_url + "/v1/auth/login/",
            status=200,
            json={"key": token},
        )
        self.responses.add(
            responses.GET,
            url=remote_url + "/v1/auth/user/",
            status=200,
            json={
                "name": "",
                "email": email,
                "suuid": fake.uuid4(),
                "is_active": True,
                "date_joined": fake.iso8601(),
                "last_login": fake.iso8601(),
            },
        )

        result = CliRunner().invoke(cli, f"login --remote {remote_url} --password {password}", input=f"{email}")

        assert "Let's login into AskAnna" in result.output
        assert "Email:" in result.output
        assert "Password:" not in result.output
        assert "logged in with" in result.output
