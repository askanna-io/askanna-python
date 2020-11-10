import requests


class Session:
    def __init__(self, *args, **kwargs):
        self.session = requests.Session()
