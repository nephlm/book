class Session(object):
    def __init__(self, novel, goal, start):
        self.novel = novel

        if goal is None:
            self.goal = 1000
        else:
            self.goal = goal

        if start is None:
            self.start = novel.count
        else:
            self.start = start

    @property
    def total_count(self):
        return self.novel.count

    @property
    def count(self):
        return self.novel.count - self.start

    @property
    def is_changed(self):
        return self.novel.is_changed
