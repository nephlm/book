class Session(object):
    def __init__(self, outline, goal, start):
        self.outline = outline

        if goal is None:
            self.goal = 1000
        else:
            self.goal = goal

        if start is None:
            self.start = outline.count
        else:
            self.start = start

    @property
    def total_count(self):
        return self.outline.count

    @property
    def count(self):
        return self.outline.count - self.start

    @property
    def is_changed(self):
        return self.outline.is_changed
