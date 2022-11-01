import unittest

from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from askanna.core.utils.validate import (
    validate_askanna_yml,
    validate_yml_environments,
    validate_yml_job_names,
)


class YAMLValidationTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_config_no_schedule(self):
        config_yml = """
test_job:
  job:
    - python test.py
"""
        config = load(config_yml, Loader=Loader)
        self.assertTrue(validate_askanna_yml(config))

    def test_config_fail_schedule(self):
        config_yml = """
test_job:
  job:
    - python test.py
  schedule:
    - "* * * * *"
    - minute: 5
    - hour: 12
      month: 11
    - often: 5
    - "* * * *"
    - "@midnight"
    - False
    - []
"""
        config = load(config_yml, Loader=Loader)
        self.assertFalse(validate_askanna_yml(config))

    def test_config_fail_schedule2(self):
        config_yml = """
test_job:
  job:
    - python test.py
  schedule:
    - "* * * *"
    - "@midnight"
    - False
    - []
"""
        config = load(config_yml, Loader=Loader)
        self.assertFalse(validate_askanna_yml(config))

    def test_config_good_schedule(self):
        config_yml = """
test_job:
  job:
    - python test.py
  schedule:
    - "* * * * *"
    - minute: 5
    - hour: 12
      month: 11
    - "@midnight"
"""
        config = load(config_yml, Loader=Loader)
        self.assertTrue(validate_askanna_yml(config))

    def test_config_invalid_timezone(self):
        config_yml = """
test_job:
  job:
    - python test.py
  schedule:
    - "* * * * *"
  timezone: "Nowhere"
"""
        config = load(config_yml, Loader=Loader)
        self.assertFalse(validate_askanna_yml(config))

    def test_config_valid_timezone(self):
        config_yml = """
test_job:
  job:
    - python test.py
  schedule:
    - "* * * * *"
  timezone: "Europe/Amsterdam"
"""
        config = load(config_yml, Loader=Loader)
        self.assertTrue(validate_askanna_yml(config))

    def test_config_bad_jobname(self):
        config_yml = """
cluster:
  job:
    - python test.py
image:
  job:
    - python test.py
"""
        config = load(config_yml, Loader=Loader)
        self.assertFalse(validate_yml_job_names(config))

    def test_config_good_jobname(self):
        config_yml = """
my-job:
  job:
    - python test.py
my-job2:
  job:
    - python test.py
"""
        config = load(config_yml, Loader=Loader)
        self.assertTrue(validate_yml_job_names(config))

    def test_config_good_jobname_nojob(self):
        config_yml = """
image:
  location: nginx:v5
"""
        config = load(config_yml, Loader=Loader)
        self.assertTrue(validate_yml_job_names(config))


class TestYMLEnvironments(unittest.TestCase):
    def test_yml_global_environment(self):
        self.assertTrue(validate_yml_environments({"environment": {"image": "askanna/python:3"}}))

        self.assertFalse(validate_yml_environments({"environment": {"something": "foo"}}))

        self.assertFalse(validate_yml_environments({"environment": "askanna/python:3"}))

    def test_job_environment(self):
        config_yml = """
test_job:
  job:
    - python test.py
  environment:
    image: python:3-slim
"""
        config = load(config_yml, Loader=Loader)
        self.assertTrue(validate_askanna_yml(config))

        config_yml = """
test_job:
  job:
    - python test.py
  environment:
    missing_image: foobar
"""
        config = load(config_yml, Loader=Loader)
        self.assertFalse(validate_askanna_yml(config))
