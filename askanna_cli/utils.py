import os
import glob


def update_available(silent_fail=True):
    """
    Check whether most recent Gitlab release of askanna_cli is newer than the
    askanna_cli version in use. If a newer version is available, return a
    link to the release on Gitlab, otherwise return ``None``.
    """
    try:
        # FIXME: some code to check the release on Gitlab
        a = None
        return a
    except Exception:
        if not silent_fail:
            raise

        # Don't let this interfere with askanna_cli usage
        return None


def check_for_project():
    """
    Performs a check if we are operating within a project folder. When
    we wish to perform a deploy action, we want to be on the same
    level with the ``setup.py`` to be able to package the file.
    """
    cwd = os.getcwd()

    pyfiles = glob.glob('*.py')

    # look for the setup.py file
    if 'setup.py' in pyfiles:
        return True

    else:
        return False
