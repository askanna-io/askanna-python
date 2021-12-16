import os
import shutil
import tempfile
import unittest
from typing import Dict

import pytest
from faker import Faker
from faker.providers import file

from askanna.config.server import DEFAULT_SERVER_CONFIG
from askanna.config.utils import (
    contains_configfile,
    read_config,
    scan_config_in_path,
    store_config,
)

fake = Faker()
fake.add_provider(file)


@pytest.fixture(autouse=True)
def change_dir():
    cwd = os.getcwd()
    yield
    os.chdir(cwd)


class TestReadConfig(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp(prefix="askanna-test-core-utils-config")

    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_read_valid_config(self):
        expected_result = {"askanna": {"remote": "https://beta-api.askanna.dev"}}

        file_content = """askanna:
  remote: https://beta-api.askanna.dev
        """

        config_file = f"{self.tempdir}/askanna_valid.yml"
        with open(config_file, "w") as f:
            f.write(file_content)

        result = read_config(config_file)
        self.assertTrue(isinstance(result, Dict))
        self.assertEqual(result, expected_result)

    def test_read_non_existing_file(self):
        config_file = f"{self.tempdir}/askanna_config_not_exist.yml"

        with self.assertRaises(SystemExit) as cm:
            read_config(config_file)

        self.assertEqual(cm.exception.code, 1)

    def test_read_invalid_config(self):
        file_content = """askanna
remote: https://beta-api.askanna.dev
        """

        config_file = f"{self.tempdir}/askanna_invalid.yml"
        with open(config_file, "w") as f:
            f.write(file_content)

        with self.assertRaises(SystemExit) as cm:
            read_config(config_file)

        self.assertEqual(cm.exception.code, 1)

    def test_read_config_type_error(self):
        with self.assertRaises(SystemExit) as cm:
            read_config(123)

        self.assertEqual(cm.exception.code, 1)


class TestStoreConfig(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp(prefix="askanna-test-core-utils-config")

    def tearDown(self):
        shutil.rmtree(self.tempdir, ignore_errors=True)

    def test_store_config(self):
        path = f'{self.tempdir}/{fake.file_name(extension="yml")}'
        store_config(path, DEFAULT_SERVER_CONFIG)
        config = read_config(path)

        self.assertTrue(isinstance(config, Dict))
        self.assertEqual(config, DEFAULT_SERVER_CONFIG)

    def test_store_config_empty(self):
        path = f'{self.tempdir}/{fake.file_name(extension="yml")}'
        store_config(path, {})
        config = read_config(path)

        self.assertTrue(isinstance(config, Dict))
        self.assertEqual(config, {})

    def test_store_overwrite(self):
        path = f'{self.tempdir}/{fake.file_name(extension="yml")}'
        config_1 = {"askanna": {"remote": "https://beta-api.askanna.eu"}}
        config_2 = {"config": "something"}

        store_config(path, config_1)
        config_read_1 = read_config(path)
        self.assertTrue(isinstance(config_read_1, Dict))
        self.assertEqual(config_read_1, config_1)

        store_config(path, config_2)
        config_read_2 = read_config(path)
        self.assertTrue(isinstance(config_read_2, Dict))
        self.assertEqual(config_read_2, config_2)


class TestContainsConfigFile(unittest.TestCase):
    def test_contains_configfile_true(self):
        dir = "tests/resources/projects/project-003-subdirectories"
        self.assertTrue(contains_configfile(dir))

    def test_contains_configfile_false(self):
        dir = "tests/resources/projects/project-003-subdirectories/src"
        self.assertFalse(contains_configfile(dir))

    def test_contains_configfile_filename_true(self):
        dir = "tests/resources/projects/project-003-subdirectories"
        filename = "README.md"
        self.assertTrue(contains_configfile(dir, filename))

    def test_contains_configfile_filename_false(self):
        dir = "tests/resources/projects/project-003-subdirectories"
        filename = "doesnotexist.txt"
        self.assertFalse(contains_configfile(dir, filename))


class TestScanConfigInPath(unittest.TestCase):
    def test_scan_config_in_path_exist(self):
        dir = "tests/resources/projects/project-003-subdirectories"
        os.chdir(dir)
        result = scan_config_in_path(os.getcwd())
        self.assertIsNot(result, "")

    def test_scan_config_in_subdirectory_exist(self):
        dir = "tests/resources/projects/project-003-subdirectories/src"
        os.chdir(dir)
        result = scan_config_in_path(os.getcwd())
        self.assertIsNot(result, "")

    def test_scan_config_in_path_not_exist(self):
        dir = "tests/resources/projects/"
        os.chdir(dir)
        result = scan_config_in_path(os.getcwd())
        self.assertIs(result, "")
