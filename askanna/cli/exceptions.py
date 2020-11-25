"""
askanna.cli specific exceptions.

Exit codes follow the sysexits.h convention:
https://www.freebsd.org/cli/man.cgi?query=sysexits&sektion=3
"""
from click import ClickException


class AskAnnaException(ClickException):
    def __init__(self, msg=None):
        super(AskAnnaException, self).__init__(msg or self.default_msg)


class AlreadyLoggedInException(AskAnnaException):
    exit_code = 0
    default_msg = ("You are already logged in. To change credentials, use "
                   "'askanna logout' first.")
