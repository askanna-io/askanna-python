import unittest
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


from askanna.core.utils import validate_yml_schedule


class YAMLValidationTest(unittest.TestCase):
    def setUp(self):
        pass

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
