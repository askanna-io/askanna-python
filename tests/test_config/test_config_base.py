import unittest

from askanna.config import config


class TestServerConfig(unittest.TestCase):
    def test_config_remote(self):
        self.assertTrue(hasattr(config.server, "remote"))
        self.assertIsNotNone(config.server.remote)

    def test_config_ui(self):
        self.assertTrue(hasattr(config.server, "ui"))
        self.assertIsNotNone(config.server.ui)

    def test_config_auth(self):
        self.assertTrue(hasattr(config.server, "token"))
        self.assertTrue(hasattr(config.server, "is_authenticated"))

    def test_config_config_dict(self):
        self.assertTrue(hasattr(config.server, "config_dict"))
        self.assertIsNotNone(config.server.config_dict)


class TestProjectConfig(unittest.TestCase):
    def test_config_project_dict(self):
        self.assertTrue(hasattr(config.project, "config_dict"))

    def test_config_project_push_target(self):
        self.assertTrue(hasattr(config.project, "push_target"))
