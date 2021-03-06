import unittest

from askanna.core.push import extract_push_target


class TestCoreUtilsExtractPushTarget(unittest.TestCase):

    def test_extract_push_target(self):
        targets = [
            ['https://beta.askanna.eu/6swz-ujcr-jQQw-SAdZ/project/6mxc-03Ew-THeb-ftGG', {
                'askanna_host': 'beta.askanna.eu',
                'http_scheme': 'https',
                'project_suuid': '6mxc-03Ew-THeb-ftGG',
                'workspace_suuid': '6swz-ujcr-jQQw-SAdZ'
            }],
            ['https://beta.askanna.eu/6swz-ujcr-jQQw-SAdZ/project/6mxc-03Ew-THeb-ftGG/', {
                'askanna_host': 'beta.askanna.eu',
                'http_scheme': 'https',
                'project_suuid': '6mxc-03Ew-THeb-ftGG',
                'workspace_suuid': '6swz-ujcr-jQQw-SAdZ'
            }],
            ['https://beta.askanna.eu/project/6mxc-03Ew-THeb-ftGG', {
                'askanna_host': 'beta.askanna.eu',
                'http_scheme': 'https',
                'project_suuid': '6mxc-03Ew-THeb-ftGG',
                'workspace_suuid': None
            }],
            ['https://beta.askanna.eu/project/6mxc-03Ew-THeb-ftGG/', {
                'askanna_host': 'beta.askanna.eu',
                'http_scheme': 'https',
                'project_suuid': '6mxc-03Ew-THeb-ftGG',
                'workspace_suuid': None
            }],
            ['http://beta.askanna.eu/project/6mxc-03Ew-THeb-ftGG/', {
                'askanna_host': 'beta.askanna.eu',
                'http_scheme': 'http',
                'project_suuid': '6mxc-03Ew-THeb-ftGG',
                'workspace_suuid': None
            }],
        ]
        for target in targets:
            self.assertDictEqual(extract_push_target(target[0]), target[1])
