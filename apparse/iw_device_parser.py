import re

from .base_parser import BaseParser


class IwDeviceParser(BaseParser):
    """Parser for a device list of the iw utility"""

    _channel_regex = re.compile(r'^(?P<channel>\d+) \((?P<frequency>\d+) MHz\)')
    _tx_power_regex = re.compile(r'^(?P<tx_power>\d+\.\d+) dBm$')

    _default_keys = (
        'mac_address',
        'ssid',
        'type',
        'channel',
        'frequency',
        'tx_power'
    )
    _parser_keys = {
        'addr': None,
        'ssid': None,
        'type': None,
        'channel': _channel_regex,
        'txpower': _tx_power_regex
    }

    def parse(self, data):
        self._data = {}
        self._current = None

        for line in data.splitlines():
            if not line or line.isspace() or ' ' not in line:
                continue

            key, value = line.lstrip().split(' ', 1)
            if key == 'Interface':
                if value in self._data:
                    raise ValueError('Duplicate device')
                self._current = value
                self._data[self._current] = {key: None for key in self._default_keys}
                continue

            if self._current is None:
                # Got a cell before the header of the table
                raise ValueError('Missing header')
            if key not in self._parser_keys:
                continue

            pattern = self._parser_keys[key]
            # If the pattern is a regex try to match it, otherwise use the raw value later
            if pattern is not None:
                match = pattern.match(value)
                if not match:
                    raise ValueError(f"Invalid value for key '{key}'")
                groups = match.groupdict()

            # Populate the data dict with available values
            if key == 'addr':
                self._data[self._current]['mac_address'] = value
            elif key == 'ssid':
                self._data[self._current]['ssid'] = value
            elif key == 'type':
                self._data[self._current]['type'] = value
            elif key == 'channel':
                self._data[self._current]['channel'] = int(groups['channel'])
                self._data[self._current]['frequency'] = int(groups['frequency'])
            elif key == 'txpower':
                self._data[self._current]['tx_power'] = float(groups['tx_power'])

        return self._data
