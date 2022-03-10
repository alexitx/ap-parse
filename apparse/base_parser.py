class BaseParser:

    _default_keys = None
    _parser_keys = None

    def __init__(self):
        self._data = None
        self._current = None

    def parse(self, data):
        raise NotImplementedError
