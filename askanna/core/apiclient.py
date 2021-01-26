import askanna
from .config import Config
from .session import Session


class Client:
    """
    Client for communication with AskAnna API service
    """

    def __init__(self, headers=None, *args, **kwargs):
        # TODO read config

        self.config = Config()
        self.headers = headers or self.generate_authenication_header()

        self.session = Session(headers=self.headers)

    def generate_authenication_header(self):
        if not self.config.user.token:
            return {}

        return {
            'user-agent': 'askanna-cli/{version}'.format(version=askanna.__version__),
            'Authorization': 'Token {token}'.format(
                token=self.config.user.token
            )
        }

    def get(self, url, **kwargs):
        return self.session.get(url, **kwargs)

    def head(self, url, **kwargs):
        return self.session.head(url, **kwargs)

    def patch(self, url, **kwargs):
        return self.session.patch(url, **kwargs)

    def post(self, url, **kwargs):
        return self.session.post(url, **kwargs)

    def create(self, url, **kwargs):
        return self.session.create(url, **kwargs)

    def delete(self, url, **kwargs):
        return self.session.delete(url, **kwargs)
