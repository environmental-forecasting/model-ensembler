import logging
import os
import resource
import sys


# Should have used a collection for this
class Arguments(object):
    class __Arguments(object):
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    instance = None

    def __init__(self, **kwargs):
        if not Arguments.instance:
            Arguments.instance = Arguments.__Arguments(**kwargs)

    def __getattr__(self, item):
        return getattr(self.instance, item)


def background_fork(double=False):
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        print("Fork failed: {} ({})".format(e.errno, e.strerror))
        sys.exit(1)

    os.setsid()

    if double:
        background_fork()
