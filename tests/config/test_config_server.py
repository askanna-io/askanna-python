import io
import os
import shutil
import sys
import tempfile
import unittest

import pytest
from faker import Faker
from faker.providers import file, internet, misc

from askanna.config.server import add_or_update_server_in_config_dict, load_config
from askanna.config.utils import store_config

fake = Faker()
fake.add_provider(internet)
fake.add_provider(misc)
fake.add_provider(file)


class TestServerConfigPath(unittest.TestCase):
    def setUp(self):
        self.environ_bck = dict(os.environ)
        self.default_config_path = os.path.expanduser("~/.askanna.yml")

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.environ_bck)

    def test_config_default_path(self):
        try:
            del sys.modules["askanna.config.server"]
        except:  # noqa # nosec
            pass
        from askanna.config.server import SERVER_CONFIG_PATH

        self.assertEqual(SERVER_CONFIG_PATH, self.default_config_path)

    def test_config_path_environment_variable(self):
        config_file = fake.file_path(extension="yml", depth=fake.random_int(min=0, max=10))
        os.environ["AA_SERVER_CONFIG_FILE"] = config_file

        try:
            del sys.modules["askanna.config.server"]
        except:  # noqa # nosec
            pass
        from askanna.config.server import SERVER_CONFIG_PATH

        self.assertEqual(SERVER_CONFIG_PATH, config_file)
        self.assertNotEqual(SERVER_CONFIG_PATH, self.default_config_path)


class TestServerName(unittest.TestCase):
    def setUp(self):
        self.environ_bck = dict(os.environ)
        self.tempdir = tempfile.mkdtemp(prefix="askanna-test-core-config-server")
        self.default_server_name = "default"

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.environ_bck)
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_config_default_path(self):
        try:
            del sys.modules["askanna.config.server"]
        except:  # noqa # nosec
            pass
        from askanna.config.server import SERVER

        self.assertEqual(SERVER, self.default_server_name)

    def test_server_config_environment_variable(self):
        server_name = fake.name()
        os.environ["AA_SERVER"] = server_name

        path = f'{self.tempdir}/{fake.file_name(extension="yml")}'
        config_dict = {
            "server": {
                server_name: {
                    "remote": "localhost",
                    "ui": "localhost",
                    "token": "localhost",
                }
            }
        }
        os.environ["AA_SERVER_CONFIG_FILE"] = path
        store_config(path, config_dict)

        try:
            del sys.modules["askanna.config.server"]
        except:  # noqa # nosec
            pass
        from askanna.config.server import SERVER

        self.assertEqual(SERVER, server_name)
        self.assertNotEqual(SERVER, self.default_server_name)


class TestLoadConfig(unittest.TestCase):
    def setUp(self):
        self.environ_bck = dict(os.environ)
        self.tempdir = tempfile.mkdtemp(prefix="askanna-test-core-config-server")

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.environ_bck)
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_load_config(self):
        config = load_config()
        self.assertIsNotNone(config.remote)

    def test_load_from_path(self):
        path = f'{self.tempdir}/{fake.file_name(extension="yml")}'
        remote_value = fake.hostname()
        ui_value = fake.hostname()
        token_value = fake.password(length=40)
        server_dict = {
            "remote": f"{remote_value}",
            "ui": f"{ui_value}",
            "token": f"{token_value}",
        }
        config_value = {
            "server": {"default": server_dict},
        }

        store_config(path, config_value)
        config = load_config(path)

        self.assertEqual(config.server, "default")
        self.assertEqual(config.remote, os.getenv("AA_REMOTE", remote_value))
        self.assertEqual(config.ui, os.getenv("AA_UI", ui_value))
        self.assertEqual(config.token, os.getenv("AA_TOKEN", token_value))
        self.assertTrue(config.is_authenticated)
        self.assertEqual(config.config_dict["server"]["default"], server_dict)

    def test_load_isnotfile(self):
        path = fake.file_path(extension="yml", depth=fake.random_int(min=0, max=10))
        config = load_config(path)
        self.assertIsNotNone(config.remote)

    def test_load_random_config(self):
        path = f'{self.tempdir}/{fake.file_name(extension="yml",)}'
        remote_value = fake.hostname()
        ui_value = fake.hostname()
        token_value = fake.password(length=40)
        config_value = {
            f"{fake.name()}": {
                "remote": f"{remote_value}",
                "ui": f"{ui_value}",
            },
            f"{fake.name()}": {
                "token": f"{token_value}",
            },
        }

        store_config(path, config_value)

        capture_output = io.StringIO()
        sys.stdout = capture_output
        config = load_config(path)

        output_value = "[INFO] We updated your AskAnna config file to support the latest features"
        self.assertNotIn(output_value, capture_output.getvalue())

        self.assertIsNotNone(config.remote)
        self.assertEqual(config.server, "default")
        self.assertNotEqual(config.remote, remote_value)
        self.assertNotEqual(config.ui, ui_value)
        self.assertNotEqual(config.token, token_value)

    def test_load_non_default_server(self):
        path = f'{self.tempdir}/{fake.file_name(extension="yml")}'
        # default server
        remote_value_default = fake.hostname()
        ui_value_default = fake.hostname()
        token_value_default = fake.password(length=40)

        # non_default server
        server_name = fake.name()
        remote_value = fake.hostname()
        ui_value = fake.hostname()
        token_value = fake.password(length=40)
        server_dict = {
            "remote": f"{remote_value}",
            "ui": f"{ui_value}",
            "token": f"{token_value}",
        }

        config_value = {
            "server": {
                "default": {
                    "remote": f"{remote_value_default}",
                    "ui": f"{ui_value_default}",
                    "token": f"{token_value_default}",
                },
                server_name: server_dict,
            },
        }

        store_config(path, config_value)
        config = load_config(path, server_name)

        self.assertEqual(config.server, server_name)
        self.assertNotEqual(config.server, "default")
        self.assertEqual(config.remote, os.getenv("AA_REMOTE", remote_value))
        self.assertNotEqual(config.remote, remote_value_default)
        self.assertEqual(config.ui, os.getenv("AA_UI", ui_value))
        self.assertNotEqual(config.ui, ui_value_default)
        self.assertEqual(config.token, os.getenv("AA_TOKEN", token_value))
        self.assertNotEqual(config.token, token_value_default)
        self.assertTrue(config.is_authenticated)
        self.assertEqual(config.config_dict["server"][server_name], server_dict)

    def test_load_non_existing_server(self):
        path = f'{self.tempdir}/{fake.file_name(extension="yml")}'
        # default server
        remote_value_default = fake.hostname()
        ui_value_default = fake.hostname()
        token_value_default = fake.password(length=40)

        # non_default server
        server_name = fake.name()
        remote_value = fake.hostname()
        ui_value = fake.hostname()
        token_value = fake.password(length=40)
        server_dict = {
            "remote": f"{remote_value}",
            "ui": f"{ui_value}",
            "token": f"{token_value}",
        }

        config_value = {
            "server": {
                "default": {
                    "remote": f"{remote_value_default}",
                    "ui": f"{ui_value_default}",
                    "token": f"{token_value_default}",
                },
                server_name: server_dict,
            },
        }

        store_config(path, config_value)
        not_existing_server = fake.name()

        capture_error = io.StringIO()
        sys.stderr = capture_error
        with pytest.raises(SystemExit):
            load_config(path, not_existing_server)

        output_value = (
            f"Server settings for '{not_existing_server}' not found. Please try again with a valid "
            "server, or add this server."
        )
        self.assertIn(output_value, capture_error.getvalue())

    def test_config_remote_environ(self):
        remote_value = fake.hostname()
        os.environ["AA_REMOTE"] = remote_value

        config = load_config()

        self.assertEqual(config.remote, remote_value)

    def test_config_ui_environ(self):
        ui_value = fake.hostname()
        os.environ["AA_UI"] = ui_value

        config = load_config()

        self.assertEqual(config.ui, ui_value)

    def test_config_token_environ(self):
        token_value = fake.password(length=40)
        os.environ["AA_TOKEN"] = token_value

        config = load_config()

        self.assertEqual(config.token, token_value)
        self.assertTrue(config.is_authenticated)

    def test_config_all_environ(self):
        remote_value = fake.hostname()
        os.environ["AA_REMOTE"] = remote_value
        ui_value = fake.hostname()
        os.environ["AA_UI"] = ui_value
        token_value = fake.password(length=40)
        os.environ["AA_TOKEN"] = token_value

        config = load_config()

        self.assertEqual(config.remote, remote_value)
        self.assertEqual(config.ui, ui_value)
        self.assertEqual(config.token, token_value)
        self.assertTrue(config.is_authenticated)


class TestAddOrUpdateServerInConfigDict(unittest.TestCase):
    def setUp(self):
        self.server_name = fake.name()
        self.remote_value_before_update = fake.hostname()
        self.ui_value_before_update = fake.hostname()
        self.token_value_before_update = fake.password(length=40)

        self.config_dict_before_update = {
            "server": {
                self.server_name: {
                    "remote": self.remote_value_before_update,
                    "ui": self.ui_value_before_update,
                    "token": self.token_value_before_update,
                }
            }
        }

    def tearDown(self):
        pass

    def test_update_existing_server(self):
        remote_value_after_update = fake.hostname()
        ui_value_after_update = fake.hostname()
        token_value_after_update = fake.password(length=40)

        config_dict_after_update = {
            "server": {
                self.server_name: {
                    "remote": remote_value_after_update,
                    "ui": ui_value_after_update,
                    "token": token_value_after_update,
                }
            }
        }

        self.assertNotEqual(self.config_dict_before_update, config_dict_after_update)

        new_config_dict = add_or_update_server_in_config_dict(
            self.config_dict_before_update,
            self.server_name,
            remote_value_after_update,
            token_value_after_update,
            ui_value_after_update,
        )

        self.assertEqual(new_config_dict, config_dict_after_update)

    def test_add_new_server(self):
        server_name_new = fake.name()
        remote_value_new = fake.hostname()
        ui_value_new = fake.hostname()
        token_value_new = ""  # nosec

        config_dict_after_update = {
            "server": {
                self.server_name: {
                    "remote": self.remote_value_before_update,
                    "ui": self.ui_value_before_update,
                    "token": self.token_value_before_update,
                },
                server_name_new: {
                    "remote": remote_value_new,
                    "ui": ui_value_new,
                    "token": token_value_new,
                },
            }
        }

        self.assertNotEqual(self.config_dict_before_update, config_dict_after_update)

        new_config_dict = add_or_update_server_in_config_dict(
            self.config_dict_before_update,
            server_name_new,
            remote_value_new,
            token_value_new,
            ui_value_new,
        )

        self.assertEqual(new_config_dict, config_dict_after_update)

    def test_add_server_config(self):
        remote_value_after_update = fake.hostname()
        ui_value_after_update = fake.hostname()
        token_value_after_update = fake.password(length=40)

        config_dict_after_update = {
            "server": {
                self.server_name: {
                    "remote": remote_value_after_update,
                    "ui": ui_value_after_update,
                    "token": token_value_after_update,
                }
            }
        }

        new_config_dict = add_or_update_server_in_config_dict(
            {},
            self.server_name,
            remote_value_after_update,
            token_value_after_update,
            ui_value_after_update,
        )

        self.assertEqual(new_config_dict, config_dict_after_update)
        self.assertNotEqual(new_config_dict, {})


class TestServerConfigFunctions(unittest.TestCase):
    def setUp(self):
        self.environ_bck = dict(os.environ)
        self.tempdir = tempfile.mkdtemp(prefix="askanna-test-core-config-server")
        self.path = f'{self.tempdir}/{fake.file_name(extension="yml")}'

        self.server_name_setup = fake.name()
        self.remote_value_setup = os.getenv("AA_REMOTE", fake.hostname())
        self.ui_value_setup = os.getenv("AA_UI", fake.hostname())
        self.token_value_setup = os.getenv("AA_TOKEN", fake.password(length=40))
        server_dict = {
            "remote": f"{self.remote_value_setup}",
            "ui": f"{self.ui_value_setup}",
            "token": f"{self.token_value_setup}",
        }
        self.config_value_setup = {
            "server": {self.server_name_setup: server_dict},
        }

        store_config(self.path, self.config_value_setup)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.environ_bck)
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_save_server_config(self):
        config = load_config(self.path, self.server_name_setup)
        self.assertEqual(config.server, self.server_name_setup)
        self.assertEqual(config.remote, self.remote_value_setup)
        self.assertEqual(config.ui, self.ui_value_setup)
        self.assertEqual(config.token, self.token_value_setup)

        config.remote = fake.hostname()
        config.ui = fake.hostname()
        config.token = fake.password(length=40)
        server_dict = {
            "remote": f"{config.remote}",
            "ui": f"{config.ui}",
            "token": f"{config.token}",
        }
        config_dict_new = {
            "server": {self.server_name_setup: server_dict},
        }
        config.config_dict = config_dict_new

        self.assertNotEqual(config.config_dict, self.config_value_setup)

        config.save_server_to_config_file()
        config_new = load_config(self.path, self.server_name_setup)

        self.assertEqual(config_new.server, config.server)
        self.assertEqual(config_new.remote, os.getenv("AA_REMOTE", config.remote))
        self.assertEqual(config_new.ui, os.getenv("AA_UI", config.ui))
        self.assertEqual(config_new.token, os.getenv("AA_TOKEN", config.token))

    def test_logout_and_remove_token(self):
        config = load_config(self.path, self.server_name_setup)
        self.assertEqual(config.server, self.server_name_setup)
        self.assertEqual(config.remote, self.remote_value_setup)
        self.assertEqual(config.ui, self.ui_value_setup)
        self.assertEqual(config.token, self.token_value_setup)

        self.assertIsNot(config.token, "")

        config.logout_and_remove_token()

        self.assertIs(config.token, "")

        config_new = load_config(self.path, self.server_name_setup)

        self.assertEqual(config_new.server, config.server)
        self.assertEqual(config_new.remote, config.remote)
        self.assertEqual(config_new.ui, config.ui)
        self.assertIs(config_new.token, os.getenv("AA_TOKEN", ""))
