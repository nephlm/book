"""
Utilities for interacting with git.
"""


import datetime
from dateutil import tz
import logging

import git

Repo = git.Repo
# from git import Repo

git_logger = logging.getLogger("git.cmd")
git_logger.setLevel(logging.INFO)


def is_repo(path):
    return get_repo(path, silent=True)


def get_repo(path, silent=False):
    try:
        return Repo(path)
    except git.InvalidGitRepositoryError:
        if not silent:
            print('No git repo found -- SKIPPING COMMIT')
        return None


def is_dirty(path):
    """
    Returns True if there are untracked files or changed files in the repo.
    """
    repo = get_repo(path)
    if repo:
        if repo.untracked_files:
            return True
        changed_files = [item.a_path for item in repo.index.diff(None)]
        if changed_files:
            return True
        return False
    else:
        return False


def commit(path):
    """
    Add and commit untracked files and changed files.  Message is the date/time in iso format.
    """
    repo = get_repo(path)
    if repo:
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
