"""
Utilities for interacting with git.
"""


import datetime
from dateutil import tz
import logging

from git import Repo

git_logger = logging.getLogger("git.cmd")
git_logger.setLevel(logging.INFO)


def is_dirty(path):
    """
    Returns True if there are untracked files or changed files in the repo.
    """
    repo = Repo(path)
    if repo.untracked_files:
        return True
    changed_files = [item.a_path for item in repo.index.diff(None)]
    if changed_files:
        return True
    return False


def commit(path):
    """
    Add and commit untracked files and changed files.  Message is the date/time in iso format.
    """
    repo = Repo(path)
    for item in repo.untracked_files:
        repo.git.add(item)
    repo.git.commit("-a", "-m", f"{aware_datetime().isoformat()}")
    repo.git.push()


def aware_datetime():
    """
    Generates a timezone aware datetime from the system timezone.
    """
    tzinfo = tz.gettz()
    return datetime.datetime.now(tz=tzinfo)
