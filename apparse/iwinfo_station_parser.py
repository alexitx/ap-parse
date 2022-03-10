import re

from .base_parser import BaseParser


class IwinfoStationParser(BaseParser):
    """Parser for a station list of the iwinfo utility"""

    _header_regex = re.compile(
        r'^(?P<mac_address>.+)  (?P<signal>\-?\d+) dBm / (?P<noise>\-?\d+) dBm '
        r'\(SNR (?P<snr>\d+)\)  (?P<inactive_time>\d+) ms ago$'
    )
    _rx_rate_regex = re.compile(
        r'^(?P<rx_rate>\d+\.\d+|unknown)(?: MBit/s)?.* '
        r'(?P<rx_packets>\d+) Pkts\.$'
    )
    _tx_rate_regex = re.compile(
        r'^(?P<tx_rate>\d+\.\d+|unknown)(?: MBit/s)?.* '
        r'(?P<tx_packets>\d+) Pkts\.$'
    )
    _throughput_regex = re.compile(r'^(?P<throughput>\d+.\d|unknown)(?: MBit/s)?$')

    _default_keys = (
        'signal',
        'noise',
        'snr',
        'inactive_time',
        'rx_rate',
        'tx_rate',
        'throughput'
    )
    _parser_keys = {
        'RX': _rx_rate_regex,
        'TX': _tx_rate_regex,
        'expected throughput': _throughput_regex
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
                    raise ValueError('Missing header')
                if ':' not in line:
                    continue

                key, value = line.lstrip().split(':', 1)
                if key not in self._parser_keys:
                    continue
                value = value.lstrip()

                pattern = self._parser_keys[key]
                if pattern is not None:
                    match = pattern.match(value)
                    if not match:
                        raise ValueError(f"Invalid value for key '{key}'")
                    groups = match.groupdict()

                if key == 'RX':
                    if groups['rx_rate'] != 'unknown':
                        rx_rate = float(groups['rx_rate'])
                    else:
                        rx_rate = None

                    self._data[self._current]['rx_rate'] = rx_rate
                    self._data[self._current]['rx_packets'] = int(groups['rx_packets'])
                elif key == 'TX':
                    if groups['tx_rate'] != 'unknown':
                        tx_rate = float(groups['tx_rate'])
                    else:
                        tx_rate = None

                    self._data[self._current]['tx_rate'] = tx_rate
                    self._data[self._current]['tx_packets'] = int(groups['tx_packets'])
                elif key == 'expected throughput':
                    if groups['throughput'] != 'unknown':
                        throughput = float(groups['throughput'])
                    else:
                        throughput = None
                    self._data[self._current]['throughput'] = throughput

                continue

            # Line is a table header

            match = self._header_regex.match(line)
            if not match:
                raise ValueError('Invalid header')
            groups = match.groupdict()
            if groups['mac_address'] in self._data:
                raise ValueError('Duplicate station')

            if groups['signal'] != 'unknown':
                signal = int(groups['signal'])
            else:
                signal = None

            if groups['noise'] != 'unknown':
                noise = int(groups['noise'])
            else:
                noise = None

            if None not in {signal, noise}:
                snr = int(groups['snr'])
            else:
                snr = None

            self._current = groups['mac_address']
            self._data[self._current] = {key: None for key in self._default_keys}
            self._data[self._current]['signal'] = signal
            self._data[self._current]['noise'] = noise
            self._data[self._current]['snr'] = snr
            self._data[self._current]['inactive_time'] = int(groups['inactive_time'])

        return self._data
