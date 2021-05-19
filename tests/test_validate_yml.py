import unittest
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


from askanna.core.utils import validate_yml_schedule, validate_yml_job_names


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
        self.assertTrue(validate_yml_schedule(config))

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
        self.assertFalse(validate_yml_schedule(config))

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
        self.assertFalse(validate_yml_schedule(config))

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
        self.assertTrue(validate_yml_schedule(config))

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
        self.assertFalse(validate_yml_schedule(config))

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
        self.assertTrue(validate_yml_schedule(config))

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
