import unittest

from apparse import parse_iw_station


class TestIwStationParser(unittest.TestCase):

    def test_valid(self):
        raw_data = (
            'Station 90:44:59:4a:44:b2 (on wlan0)\n'
            '        inactive time:  2830 ms\n'
            '        rx bytes:       415320\n'
            '        rx packets:     2792\n'
            '        tx bytes:       1217519\n'
            '        tx packets:     1648\n'
            '        tx retries:     77\n'
            '        tx failed:      49\n'
            '        rx drop misc:   0\n'
            '        signal:         -66 [-69, -69, -82] dBm\n'
            '        signal avg:     -62 [-66, -64, -76] dBm\n'
            '        tx bitrate:     7.2 MBit/s\n'
            '        rx bitrate:     59.6 MBit/s\n'
            '        rx duration:    267680 us\n'
            '        last ack signal:-95 dBm\n'
            '        authorized:     yes\n'
            '        authenticated:  yes\n'
            '        associated:     yes\n'
            '        preamble:       short\n'
            '        WMM/WME:        yes\n'
            '        MFP:            no\n'
            '        TDLS peer:      no\n'
            '        DTIM period:    2\n'
            '        beacon interval:100\n'
            '        short preamble: yes\n'
            '        short slot time:yes\n'
            '        connected time: 1964 seconds\n\n'
            'Station f4:1a:29:64:55:5a (on wlan1)\n'
            '        inactive time:  50 ms\n'
            '        rx bytes:       14483244\n'
            '        rx packets:     70548\n'
            '        tx bytes:       380501678\n'
            '        tx packets:     294116\n'
            '        tx retries:     5174\n'
            '        tx failed:      0\n'
            '        rx drop misc:   64\n'
            '        signal:         -51 [-53, -55, -73] dBm\n'
            '        signal avg:     -51 [-53, -54, -73] dBm\n'
            '        tx bitrate:     12.3 MBit/s MCS 7 short GI\n'
            '        rx bitrate:     65.1 MBit/s MCS 7\n'
            '        rx duration:    0 us\n'
            '        expected throughput:    47.507Mbps\n'
            '        authorized:     yes\n'
            '        authenticated:  yes\n'
            '        associated:     yes\n'
            '        preamble:       short\n'
            '        WMM/WME:        yes\n'
            '        MFP:            no\n'
            '        TDLS peer:      no\n'
            '        DTIM period:    2\n'
            '        beacon interval:100\n'
            '        short preamble: yes\n'
            '        short slot time:yes\n'
            '        connected time: 6490 seconds\n'
        )
        expected_data = {
            '90:44:59:4a:44:b2': {
                'device': 'wlan0',
                'inactive_time': 2830,
                'rx_bytes': 415320,
                'rx_packets': 2792,
                'tx_bytes': 1217519,
                'tx_packets': 1648,
                'tx_retries': 77,
                'tx_failed': 49,
                'rx_drop_misc': 0,
                'signal': -66,
                'signal_avg': -62,
                'tx_bitrate': 7.2,
                'rx_bitrate': 59.6,
                'rx_duration': 267680,
                'last_ack_signal': -95,
                'expected_throughput': None,
                'authorized': True,
                'authenticated': True,
                'associated': True,
                'preamble': 'short',
                'wmm_wme': True,
                'mfp': False,
                'tdls_peer': False,
                'dtim_period': 2,
                'beacon_interval': 100,
                'short_preamble': True,
                'short_slot_time': True,
                'connected_time': 1964
            },
            'f4:1a:29:64:55:5a': {
                'device': 'wlan1',
                'inactive_time': 50,
                'rx_bytes': 14483244,
                'rx_packets': 70548,
                'tx_bytes': 380501678,
                'tx_packets': 294116,
                'tx_retries': 5174,
                'tx_failed': 0,
                'rx_drop_misc': 64,
                'signal': -51,
                'signal_avg': -51,
                'tx_bitrate': 12.3,
                'rx_bitrate': 65.1,
                'rx_duration': 0,
                'last_ack_signal': None,
                'expected_throughput': 47.507,
                'authorized': True,
                'authenticated': True,
                'associated': True,
                'preamble': 'short',
                'wmm_wme': True,
                'mfp': False,
                'tdls_peer': False,
                'dtim_period': 2,
                'beacon_interval': 100,
                'short_preamble': True,
                'short_slot_time': True,
                'connected_time': 6490
            }
        }
        parsed_data = parse_iw_station(raw_data)
        self.assertEqual(parsed_data, expected_data)

    def test_invalid(self):
        raw_data = (
            'Station 90:44:59:4a:44:b2 (on wlan0)\n'
            '        inactive time:  -2830 ms\n'
            '        rx bytes:       invalid\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iw_station(raw_data)
        self.assertEqual(str(ctx.exception), "Invalid value for key 'inactive time'")

    def test_missing_header(self):
        raw_data = (
            '        inactive time:  2830 ms\n'
            '        rx bytes:       415320\n'
            '        rx packets:     2792\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iw_station(raw_data)
        self.assertEqual(str(ctx.exception), 'Missing header')

    def test_invalid_header(self):
        raw_data = (
            'Invalid Station 90:44:59:4a:44:b2 (-)\n'
            '        inactive time:  2830 ms\n'
            '        rx bytes:       415320\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iw_station(raw_data)
        self.assertEqual(str(ctx.exception), 'Invalid header')

    def test_duplicate_station(self):
        raw_data = (
            'Station 90:44:59:4a:44:b2 (on wlan0)\n'
            '        inactive time:  2830 ms\n'
            '        rx bytes:       415320\n\n'
            'Station 90:44:59:4a:44:b2 (on wlan0)\n'
            '        inactive time:  50 ms\n'
            '        rx bytes:       14483244\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iw_station(raw_data)
        self.assertEqual(str(ctx.exception), 'Duplicate station')
