# This is a temporary workaround till Poetry supports scripts, see
# https://github.com/sdispater/poetry/issues/241.
from subprocess import check_call


def start():
    check_call(["python", "run.py"])


def test():
    check_call(["python", "-m", "unittest", "discover", "tests"])
