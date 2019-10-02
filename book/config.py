import os.path

import yaml


class Config(object):

    DEFAULT_KEYS = ("tiddlywiki",)

    def __init__(self, path=None):
        if path is None:
            path = "config.yaml"

        for key in self.DEFAULT_KEYS:
            setattr(self, key, None)

        with open(path, "r") as fp:
            self._conf = yaml.safe_load(fp.read())
            for key in self._conf:
                setattr(self, key, self._conf[key])


def get_config(path):
    # Might do some path massaging later on.
    if os.path.splitext(path) != ".yaml":
        path = os.path.join(path, "config.yaml")
    return Config(path)
