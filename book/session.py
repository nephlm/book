"""
Class to track changes as edits are happening.  It is used to track words and to commit changes to git.

Right now git is not optional.  If the novel does not have a backing git repo or if keys are not set up
it will probably throw an error. 

Neutering `is_changed()` and `commit()` will fix this. 
"""

import time

import book.git_utils as git_utils


class Session(object):

    COMMIT_THRESHOLD = 600
    CHANGE_THRESHOLD = 5

    def __init__(self, novel, goal, start):
        self.novel = novel
        self.last_commit = time.time()
        self.last_change = 0

        if goal is None:
            self.goal = 1000
        else:
            self.goal = goal

        if start is None:
            self.start = novel.outline.count
        else:
            self.start = start

    @property
    def total_count(self):
        return self.novel.outline.count

    @property
    def count(self):
        return self.novel.outline.count - self.start

    @property
    def is_changed(self):
        changed = self.novel.outline.is_changed
        if changed:
            self.last_change = time.time()
        return changed

    def commit(self):
        # print(
        #     f"{time.time() - self.last_commit} || {time.time() - self.last_change} || {git_utils.is_dirty(self.novel.path)}"
        # )
        if not git_utils.is_repo(self.novel.path):
            # No git repo, skip
            return

        commit_delta = time.time() - self.last_commit
        change_delta = time.time() - self.last_change
        if (
            change_delta > self.CHANGE_THRESHOLD
            and commit_delta > self.COMMIT_THRESHOLD
            and git_utils.is_dirty(self.novel.path)
        ):
            self.do_commit()

    def do_commit(self):
        print("\ncommiting")
        git_utils.commit(self.novel.path)
        self.last_commit = time.time()
