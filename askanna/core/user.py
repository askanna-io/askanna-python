class User:
    def __init__(self, *args, **kwargs):
        self.user = None
        self.token = kwargs.get('token')

    @property
    def authenticated(self):
        return self.token is not None
