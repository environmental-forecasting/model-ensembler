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

