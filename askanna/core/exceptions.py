class Error(Exception):
    pass


class CreateError(Error):
    pass


class ConnectionError(Error):
    pass


class DeleteError(Error):
    pass


class GetError(Error):
    pass


class HeadError(Error):
    pass


class PostError(Error):
    pass


class PatchError(Error):
    pass


class PutError(Error):
    pass


class RunError(Error):
    pass


class MultipleObjectsReturned(Error):
    """The query returned multiple objects when only one was expected."""

    pass
