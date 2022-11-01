import json

import requests
from requests.structures import CaseInsensitiveDict

from askanna import USING_ASKANNA_CLI
from askanna import __version__ as askanna_version
from askanna.config import config
from askanna.config.api_url import askanna_url
from askanna.core.exceptions import ConnectionError
from askanna.core.utils.object import json_serializer


class Client:
    """
    Client for communication with AskAnna API service
    """

    def __init__(self):
        self.config = config
        self.askanna_url = askanna_url
        self.session = requests.Session()
        self.session.headers.update(self.generate_authenication_header())

    def generate_authenication_header(self) -> CaseInsensitiveDict:
        askanna_agent = USING_ASKANNA_CLI and "cli" or "python-sdk"
        auth_header = CaseInsensitiveDict(
            {
                "askanna-agent": askanna_agent,
                "askanna-agent-version": askanna_version,
                "user-agent": f"askanna-python/{askanna_version}",
            }
        )

        if self.config.server.is_authenticated:
            auth_header.update({"Authorization": f"Token {self.config.server.token}"})

        return auth_header

    def update_session(self):
        self.session.headers.update(self.generate_authenication_header())

    def _connection_error_message(self, url, error):
        connection_error_message_base = "Something went wrong. Please check whether the URL is an AskAnna Backend."
        return f"{connection_error_message_base}\n    URL:    {url}\n    Error: {error}"

    def get(self, url, **kwargs):
        try:
            return self.session.get(url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(self._connection_error_message(url, e))

    def head(self, url, **kwargs):
        try:
            return self.session.head(url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(self._connection_error_message(url, e))

    def patch(self, url, **kwargs):
        if kwargs.get("json"):
            kwargs["json"] = json.loads(json.dumps(kwargs.get("json"), default=json_serializer))

        try:
            return self.session.patch(url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(self._connection_error_message(url, e))

    def put(self, url, **kwargs):
        if kwargs.get("json"):
            kwargs["json"] = json.loads(json.dumps(kwargs.get("json"), default=json_serializer))

        try:
            return self.session.put(url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(self._connection_error_message(url, e))

    def post(self, url, **kwargs):
        if kwargs.get("json"):
            kwargs["json"] = json.loads(json.dumps(kwargs.get("json"), default=json_serializer))

        try:
            return self.session.post(url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(self._connection_error_message(url, e))

    def create(self, url, **kwargs):
        return self.post(url, **kwargs)

    def delete(self, url, **kwargs):
        if kwargs.get("json"):
            kwargs["json"] = json.loads(json.dumps(kwargs.get("json"), default=json_serializer))

        try:
            return self.session.delete(url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(self._connection_error_message(url, e))


client = Client()
