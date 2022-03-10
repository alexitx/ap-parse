import re

from .base_parser import BaseParser


class IwinfoDeviceParser(BaseParser):
    """Parser for a device list of the iwinfo utility"""

    _header_regex = re.compile(r'^(?P<device_name>[^ ]+) +ESSID: \"(?P<ssid>.+)\"$')
    _mode_regex = re.compile(
        r'^(?P<mode>.+)  Channel: (?P<channel>\d+|unknown) '
        r'\((?P<frequency>\d\.\d+|unknown)(?: GHz)?\)$'
    )
    _tx_power_regex = re.compile(
        r'^(?P<tx_power>\d+|unknown)(?: dBm)?  '
        r'Link Quality: (?P<quality>\d+|unknown)/(?P<max_quality>\d+|unknown)$'
    )
    _signal_regex = re.compile(
        r'^(?P<signal>-?\d+|unknown)(?: dBm)?  '
        r'Noise: (?P<noise>-?\d+|unknown)(?: dBm)?$'
    )
    _bitrate_regex = re.compile(r'^(?P<bitrate>\d+.\d|unknown)(?: MBit/s)?$')
    _encryption_regex = re.compile(r'^(?P<encryption>.+)$')
    _type_regex = re.compile(r'^(?P<type>.+)  HW Mode\(s\): (?P<modes>.+)$')
    _hardware_regex = re.compile(r'^(?P<hw_id>.+) \[(?P<hw_name>.+)\]$')
    _vap_support_regex = re.compile(r'^(?P<vap_support>yes|no)  PHY name: (?P<phy_name>.+)$')

    _default_keys = (
        'ssid',
        'mac_address',
        'mode',
        'channel',
        'frequency',
        'tx_power',
        'quality',
        'signal',
        'noise',
        'bitrate',
        'encryption',
        'type',
        'modes',
        'hardware_id',
        'hardware_name',
        'vap_support',
        'phy_name'
    )
    _parser_keys = {
        'Access Point': None,
        'Mode': _mode_regex,
        'Tx-Power': _tx_power_regex,
        'Signal': _signal_regex,
        'Bit Rate': _bitrate_regex,
        'Encryption': _encryption_regex,
        'Type': _type_regex,
        'Hardware': _hardware_regex,
        'Supports VAPs': _vap_support_regex
    }

    def parse(self, data):
        self._data = {}
        self._current = None

        for line in data.splitlines():
            if not line or line.isspace():
                continue

            if line[0] in {' ', '\t'}:
                # Line is a table body

                if self._current is None:
                    # Got a cell before the header of the table
                    raise ValueError('Missing header')
                if ':' not in line:
                    continue

                key, value = line.lstrip().split(':', 1)
                if key not in self._parser_keys:
                    continue
                value = value.lstrip()

                pattern = self._parser_keys[key]
                # If the pattern is a regex try to match it, otherwise use the raw value later
                if pattern is not None:
                    match = pattern.match(value)
                    if not match:
                        raise ValueError(f"Invalid value for key '{key}'")
                    groups = match.groupdict()

                # Populate the data dict with available values
                if key == 'Access Point':
                    self._data[self._current]['mac_address'] = value
                elif key == 'Mode':
                    if groups['channel'] != 'unknown':
                        channel = int(groups['channel'])
                    else:
                        channel = None

                    if groups['frequency'] != 'unknown':
                        freq = int(float(groups['frequency']) * 1000)
                    else:
                        freq = None

                    self._data[self._current]['mode'] = groups['mode']
                    self._data[self._current]['channel'] = channel
                    self._data[self._current]['frequency'] = freq
                elif key == 'Tx-Power':
                    if groups['tx_power'] != 'unknown':
                        tx_power = int(groups['tx_power'])
                    else:
                        tx_power = None

                    if 'unknown' not in {groups['quality'], groups['max_quality']}:
                        quality = int(groups['quality']) * 100 // int(groups['max_quality'])
                    else:
                        quality = None

                    self._data[self._current]['tx_power'] = tx_power
                    self._data[self._current]['quality'] = quality
                elif key == 'Signal':
                    if groups['signal'] != 'unknown':
                        signal = int(groups['signal'])
                    else:
                        signal = None

                    if groups['noise'] != 'unknown':
                        noise = int(groups['noise'])
                    else:
                        noise = None

                    self._data[self._current]['signal'] = signal
                    self._data[self._current]['noise'] = noise
                elif key == 'Bit Rate':
                    if groups['bitrate'] != 'unknown':
                        bitrate = float(groups['bitrate'])
                    else:
                        bitrate = None
                    self._data[self._current]['bitrate'] = bitrate
                elif key == 'Encryption':
                    self._data[self._current]['encryption'] = groups['encryption']
                elif key == 'Type':
                    self._data[self._current]['type'] = groups['type']
                    self._data[self._current]['modes'] = groups['modes']
                elif key == 'Hardware':
                    if groups['hw_id'] != 'unknown':
                        hw_id = groups['hw_id']
                    else:
                        hw_id = None

                    if groups['hw_name'] != 'unknown':
                        hw_name = groups['hw_name']
                    else:
                        hw_name = None

                    self._data[self._current]['hardware_id'] = hw_id
                    self._data[self._current]['hardware_name'] = hw_name
                elif key == 'Supports VAPs':
                    self._data[self._current]['vap_support'] = groups['vap_support'] == 'yes'
                    self._data[self._current]['phy_name'] = groups['phy_name']

                continue

            # Line is a table header

            match = self._header_regex.match(line)
            if not match:
                raise ValueError('Invalid header')
            groups = match.groupdict()
            if groups['device_name'] in self._data:
                raise ValueError('Duplicate device')

            self._current = groups['device_name']
            self._data[self._current] = {key: None for key in self._default_keys}
            self._data[self._current]['ssid'] = groups['ssid']

        return self._data
