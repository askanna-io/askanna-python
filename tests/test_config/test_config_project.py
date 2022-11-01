import os
import unittest
from typing import Dict

import pytest

from askanna.config.project import PushTarget, extract_push_target, load_config


@pytest.fixture(autouse=True)
def change_dir():
    cwd = os.getcwd()
    yield
    os.chdir(cwd)


class TestProjectConfig(unittest.TestCase):
    def test_load_project_config(self):
        config = load_config()
        self.assertIs(config.push_target.url, "")

    def test_load_project_config_file(self):
        project_config_path = "tests/fixtures/projects/project-003-subdirectories/askanna.yml"

        config = load_config(project_config_path)

        self.assertIsInstance(config.config_dict, Dict)
        self.assertIsNot(config.config_dict, {})
        self.assertEqual(
            config.push_target.url, "https://beta.askanna.eu/2Bd3-fHXM-Lf22-Xne7/project/3FtY-Bb1W-Kj1m-ZAED"
        )
        self.assertEqual(config.workspace_suuid, "2Bd3-fHXM-Lf22-Xne7")
        self.assertEqual(config.project_suuid, "3FtY-Bb1W-Kj1m-ZAED")

    def test_load_project_config_no_push_target(self):
        project_config_path = "tests/fixtures/projects/project-001-simple/askanna.yml"

        config = load_config(project_config_path)

        self.assertIsInstance(config.config_dict, Dict)
        self.assertIsNot(config.config_dict, {})
        self.assertIs(config.push_target.url, "")
        self.assertIs(config.workspace_suuid, "")
        self.assertIs(config.project_suuid, "")


class TestExtractPushTarget(unittest.TestCase):
    def test_extract_push_target(self):
        http_scheme = "https"
        host = "beta.askanna.eu"
        workspace_suuid = "6swz-ujcr-jQQw-SAdZ"
        project_suuid = "6mxc-03Ew-THeb-ftGG"

        push_target = f"{http_scheme}://{host}/{workspace_suuid}/project/{project_suuid}"
        push_target_2 = f"{http_scheme}://{host}/{workspace_suuid}/project/{project_suuid}/"

        expected_result = PushTarget(
            url=push_target,
            http_scheme=http_scheme,
            host=host,
            workspace_suuid=workspace_suuid,
            project_suuid=project_suuid,
        )
        expected_result_2 = PushTarget(
            url=push_target_2,
            http_scheme=http_scheme,
            host=host,
            workspace_suuid=workspace_suuid,
            project_suuid=project_suuid,
        )

        result = extract_push_target(push_target)
        result_2 = extract_push_target(push_target_2)

        self.assertEqual(result, expected_result)
        self.assertEqual(result_2, expected_result_2)

    def test_extract_push_target_http(self):
        http_scheme = "http"
        host = "beta.askanna.eu"
        workspace_suuid = "6swz-ujcr-jQQw-SAdZ"
        project_suuid = "6mxc-03Ew-THeb-ftGG"

        push_target = f"{http_scheme}://{host}/{workspace_suuid}/project/{project_suuid}"
        push_target_2 = f"{http_scheme}://{host}/{workspace_suuid}/project/{project_suuid}/"

        expected_result = PushTarget(
            url=push_target,
            http_scheme=http_scheme,
            host=host,
            workspace_suuid=workspace_suuid,
            project_suuid=project_suuid,
        )
        expected_result_2 = PushTarget(
            url=push_target_2,
            http_scheme=http_scheme,
            host=host,
            workspace_suuid=workspace_suuid,
            project_suuid=project_suuid,
        )

        result = extract_push_target(push_target)
        result_2 = extract_push_target(push_target_2)

        self.assertEqual(result, expected_result)
        self.assertEqual(result_2, expected_result_2)

    def test_extract_push_target_no_workspace(self):
        http_scheme = "https"
        host = "beta-api.askanna.eu"
        project_suuid = "6mxc-03Ew-THeb-ftGG"

        push_target = f"{http_scheme}://{host}/project/{project_suuid}"
        push_target_2 = f"{http_scheme}://{host}/project/{project_suuid}/"

        expected_result = PushTarget(
            url=push_target,
            http_scheme=http_scheme,
            host=host,
            workspace_suuid=None,
            project_suuid=project_suuid,
        )
        expected_result_2 = PushTarget(
            url=push_target_2,
            http_scheme=http_scheme,
            host=host,
            workspace_suuid=None,
            project_suuid=project_suuid,
        )

        result = extract_push_target(push_target)
        result_2 = extract_push_target(push_target_2)

        self.assertEqual(result, expected_result)
        self.assertEqual(result_2, expected_result_2)

    def test_extract_push_target_not_set(self):
        with pytest.raises(ValueError):
            extract_push_target("")

    def test_extract_not_valid_push_target(self):
        with pytest.raises(ValueError):
            extract_push_target("https://example.com/")
