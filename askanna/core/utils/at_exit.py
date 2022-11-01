# Code for exiting in iPython. Inspiration from https://stackoverflow.com/a/40222538
# exit_register runs at the end of ipython %run or the end of the Python interpreter
try:
    ip = get_ipython()  # type: ignore
except NameError:
    from atexit import register as exit_register  # noqa: F401
else:
    from functools import wraps

    def exit_register(func, *args, **kwargs):
        """Decorator that registers a post_execute for IPython. After its execution, it unregisters itself for
        subsequent runs."""

        @wraps(func)
        def wrapper():
            func(*args, **kwargs)
            ip.events.unregister("post_execute", wrapper)

        ip.events.register("post_execute", wrapper)
        return wrapper
