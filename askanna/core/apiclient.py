import json

from askanna import (
    __version__ as askanna_version,
    USING_ASKANNA_CLI,
)
from .config import Config
from .session import Session
from .utils import json_serializer


class Client:
    """
    Client for communication with AskAnna API service
    """

    def __init__(self, headers=None, *args, **kwargs):
        self.config = Config()
        self.headers = headers or self.generate_authenication_header()
        self.session = Session(headers=self.headers)

    def generate_authenication_header(self):
        if not self.config.user.token:
            return {}

        askanna_agent = USING_ASKANNA_CLI and "cli" or "python-sdk"

        return {
            "askanna-agent": askanna_agent,
            "askanna-agent-version": askanna_version,
            "user-agent": f"askanna-python/{askanna_version}",
            "Authorization": f"Token {self.config.user.token}",
        }

    def get(self, url, **kwargs):
        return self.session.get(url, **kwargs)

    def head(self, url, **kwargs):
        return self.session.head(url, **kwargs)

    def patch(self, url, **kwargs):
        if kwargs.get("json"):
            kwargs["json"] = json.loads(
                json.dumps(kwargs.get("json"), default=json_serializer)
            )
        return self.session.patch(url, **kwargs)

    def put(self, url, **kwargs):
        if kwargs.get("json"):
            kwargs["json"] = json.loads(
                json.dumps(kwargs.get("json"), default=json_serializer)
            )
        return self.session.put(url, **kwargs)

    def post(self, url, **kwargs):
        if kwargs.get("json"):
            kwargs["json"] = json.loads(
                json.dumps(kwargs.get("json"), default=json_serializer)
            )
        return self.session.post(url, **kwargs)

    def create(self, url, **kwargs):
        if kwargs.get("json"):
            kwargs["json"] = json.loads(
                json.dumps(kwargs.get("json"), default=json_serializer)
            )
        return self.session.create(url, **kwargs)

    def delete(self, url, **kwargs):
        if kwargs.get("json"):
            kwargs["json"] = json.loads(
                json.dumps(kwargs.get("json"), default=json_serializer)
            )
        return self.session.delete(url, **kwargs)
