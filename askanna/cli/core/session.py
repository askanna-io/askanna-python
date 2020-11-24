import requests


class Session:
    def __init__(self, headers=None, *args, **kwargs):
        self.session = requests.Session()

        if headers:
            self.session.headers.update(headers)

    def get(self, url, **kwargs):
        return self.session.get(url, **kwargs)

    def head(self, url, **kwargs):
        return self.session.head(url, **kwargs)

    def patch(self, url, **kwargs):
        return self.session.patch(url, **kwargs)

    def post(self, url, **kwargs):
        return self.session.post(url, **kwargs)

    def create(self, url, **kwargs):
        return self.post(url, **kwargs)

    def delete(self, url, **kwargs):
        return self.session.delete(url, **kwargs)
