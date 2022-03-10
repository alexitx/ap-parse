class BaseParser:
    """Base class for parsers"""

    _default_keys = None
    _parser_keys = None

    def __init__(self):
        self._data = None
        self._current = None

    def parse(self, data):
        """
        Parse the command output string

        Args:
            data (str): Command output

        Returns:
            dict: Parsed data

        Raises:
            ValueError: Missing, invalid or duplicate values
        """

        raise NotImplementedError
