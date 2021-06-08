import unittest

from askanna import config
from askanna.settings import CONFIG_ASKANNA_REMOTE


class TestAskAnnaConfig(unittest.TestCase):

    def test_config_remote_default(self):
        self.assertEqual(config.remote, CONFIG_ASKANNA_REMOTE.get("askanna").get("remote"))

    def test_config_before_login(self):
        self.assertEqual(config.user.token, None)
        self.assertFalse(config.user.authenticated)

    def test_config_push_target_no_project(self):
        self.assertEqual(config.push_target, None)

    def test_config_workspace_suuid_no_project(self):
        self.assertEqual(config.workspace_suuid, None)

    def test_config_project_suuid_no_project(self):
        self.assertEqual(config.project_suuid, None)
