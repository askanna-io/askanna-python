from askanna_cli.core.config import Config
from askanna_cli.core.session import Session


class Client:
    """
    Client for communication with AskAnna API service
    """

    def __init__(self, *args, **kwargs):
        # TODO read config

        self.config = Config()
        self.session = Session()
