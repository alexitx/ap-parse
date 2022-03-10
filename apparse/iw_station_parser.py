import re

from .base_parser import BaseParser


class IwStationParser(BaseParser):
    """Parser for a station list of the iw utility"""

    _header_regex = re.compile(r'^Station (?P<mac_address>.+) \(on (?P<device>.+)\)$')
    _inactive_time_regex = re.compile(r'^(?P<inactive_time>\d+) ms$')
    _int_regex = re.compile(r'^(?P<int>\d+)$')
    _bool_regex = re.compile(r'^(?P<bool>yes|no)$')
    _signal_regex = re.compile(r'^(?P<signal>-?\d+).* dBm$')
    _bitrate_regex = re.compile(r'^(?P<bitrate>\d+\.\d) MBit/s')
    _rx_duration_regex = re.compile(r'^(?P<rx_duration>\d+) us$')
    _throughput_regex = re.compile(r'^(?P<throughput>\d+.\d+)Mbps$')
    _connected_time_regex = re.compile(r'^(?P<connected_time>\d+) seconds$')

    _default_keys = (
        'device',
        'inactive_time',
        'rx_bytes',
        'rx_packets',
        'tx_bytes',
        'tx_packets',
        'tx_retries',
        'tx_failed',
        'rx_drop_misc',
        'signal',
        'signal_avg',
        'tx_bitrate',
        'rx_bitrate',
        'rx_duration',
        'last_ack_signal',
        'expected_throughput',
        'authorized',
        'authenticated',
        'associated',
        'preamble',
        'wmm_wme',
        'mfp',
        'tdls_peer',
        'dtim_period',
        'beacon_interval',
        'short_preamble',
        'short_slot_time',
        'connected_time',
    )
    _parser_keys = {
        'inactive time': _inactive_time_regex,
        'rx bytes': _int_regex,
        'rx packets': _int_regex,
        'tx bytes': _int_regex,
        'tx packets': _int_regex,
        'tx retries': _int_regex,
        'tx failed': _int_regex,
        'rx drop misc': _int_regex,
        'signal': _signal_regex,
        'signal avg': _signal_regex,
        'tx bitrate': _bitrate_regex,
        'rx bitrate': _bitrate_regex,
        'rx duration': _rx_duration_regex,
        'last ack signal': _signal_regex,
        'expected throughput': _throughput_regex,
        'authorized': _bool_regex,
        'authenticated': _bool_regex,
        'associated': _bool_regex,
        'preamble': None,
        'WMM/WME': _bool_regex,
        'MFP': _bool_regex,
        'TDLS peer': _bool_regex,
        'DTIM period': _int_regex,
        'beacon interval': _int_regex,
        'short preamble': _bool_regex,
        'short slot time': _bool_regex,
        'connected time': _connected_time_regex
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
                if key == 'inactive time':
                    self._data[self._current]['inactive_time'] = int(groups['inactive_time'])
                elif key == 'rx bytes':
                    self._data[self._current]['rx_bytes'] = int(groups['int'])
                elif key == 'rx packets':
                    self._data[self._current]['rx_packets'] = int(groups['int'])
                elif key == 'tx bytes':
                    self._data[self._current]['tx_bytes'] = int(groups['int'])
                elif key == 'tx packets':
                    self._data[self._current]['tx_packets'] = int(groups['int'])
                elif key == 'tx retries':
                    self._data[self._current]['tx_retries'] = int(groups['int'])
                elif key == 'tx failed':
                    self._data[self._current]['tx_failed'] = int(groups['int'])
                elif key == 'rx drop misc':
                    self._data[self._current]['rx_drop_misc'] = int(groups['int'])
                elif key == 'signal':
                    self._data[self._current]['signal'] = int(groups['signal'])
                elif key == 'signal avg':
                    self._data[self._current]['signal_avg'] = int(groups['signal'])
                elif key == 'tx bitrate':
                    self._data[self._current]['tx_bitrate'] = float(groups['bitrate'])
                elif key == 'rx bitrate':
                    self._data[self._current]['rx_bitrate'] = float(groups['bitrate'])
                elif key == 'rx duration':
                    self._data[self._current]['rx_duration'] = int(groups['rx_duration'])
                elif key == 'last ack signal':
                    self._data[self._current]['last_ack_signal'] = int(groups['signal'])
                elif key == 'expected throughput':
                    self._data[self._current]['expected_throughput'] = float(groups['throughput'])
                elif key == 'authorized':
                    self._data[self._current]['authorized'] = groups['bool'] == 'yes'
                elif key == 'authenticated':
                    self._data[self._current]['authenticated'] = groups['bool'] == 'yes'
                elif key == 'associated':
                    self._data[self._current]['associated'] = groups['bool'] == 'yes'
                elif key == 'preamble':
                    self._data[self._current]['preamble'] = value
                elif key == 'WMM/WME':
                    self._data[self._current]['wmm_wme'] = groups['bool'] == 'yes'
                elif key == 'MFP':
                    self._data[self._current]['mfp'] = groups['bool'] == 'yes'
                elif key == 'TDLS peer':
                    self._data[self._current]['tdls_peer'] = groups['bool'] == 'yes'
                elif key == 'DTIM period':
                    self._data[self._current]['dtim_period'] = int(groups['int'])
                elif key == 'beacon interval':
                    self._data[self._current]['beacon_interval'] = int(groups['int'])
                elif key == 'short preamble':
                    self._data[self._current]['short_preamble'] = groups['bool'] == 'yes'
                elif key == 'short slot time':
                    self._data[self._current]['short_slot_time'] = groups['bool'] == 'yes'
                elif key == 'connected time':
                    self._data[self._current]['connected_time'] = int(groups['connected_time'])

                continue

            # Line is a table header

            match = self._header_regex.match(line)
            if not match:
                raise ValueError('Invalid header')
            groups = match.groupdict()
            if groups['mac_address'] in self._data:
                raise ValueError('Duplicate station')

            self._current = groups['mac_address']
            self._data[self._current] = {key: None for key in self._default_keys}
            self._data[self._current]['device'] = groups['device']

        return self._data
