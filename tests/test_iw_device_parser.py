import unittest

from apparse import parse_iw_device


class TestIwDeviceParser(unittest.TestCase):

    def test_valid(self):
        raw_data = (
            'Interface wlan0\n'
            '        ifindex 18\n'
            '        wdev 0x2\n'
            '        addr 63:85:a6:21:68:01\n'
            '        ssid Access Point 5GHz SSID\n'
            '        type AP\n'
            '        wiphy 0\n'
            '        channel 44 (5220 MHz), width: 80 MHz, center1: 5220 MHz\n'
            '        txpower 23.00 dBm\n'
            '        multicast TXQ:\n'
            '                qsz-byt qsz-pkt flows   drops   marks   overlmt hashcol tx-bytes        tx-packets\n'
            '                0       0       77588   0       0       0       0       34894147                77588\n\n'
            'Interface wlan1\n'
            '        ifindex 17\n'
            '        wdev 0x100000002\n'
            '        addr ce:91:1c:58:d5:0c\n'
            '        ssid Access Point 2.4GHz SSID\n'
            '        type AP\n'
            '        wiphy 1\n'
            '        channel 10 (2457 MHz), width: 20 MHz, center1: 2457 MHz\n'
            '        txpower 17.00 dBm\n'
            '        multicast TXQ:\n'
            '                qsz-byt qsz-pkt flows   drops   marks   overlmt hashcol tx-bytes        tx-packets\n'
            '                0       0       39459   0       0       0       0       19634313                50617\n'
        )
        expected_data = {
            'wlan0': {
                'mac_address': '63:85:a6:21:68:01',
                'ssid': 'Access Point 5GHz SSID',
                'type': 'AP',
                'channel': 44,
                'frequency': 5220,
                'tx_power': 23.0
            },
            'wlan1': {
                'mac_address': 'ce:91:1c:58:d5:0c',
                'ssid': 'Access Point 2.4GHz SSID',
                'type': 'AP',
                'channel': 10,
                'frequency': 2457,
                'tx_power': 17.0
            }
        }
        parsed_data = parse_iw_device(raw_data)
        self.assertEqual(parsed_data, expected_data)

    def test_invalid(self):
        raw_data = (
            'Interface wlan0\n'
            '        channel -1 (invalid MHz), width: - MHz, center1: 5220 MHz\n'
            '        txpower 0 dBm\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iw_device(raw_data)
        self.assertEqual(str(ctx.exception), "Invalid value for key 'channel'")

    def test_missing_header(self):
        raw_data = (
            '        ifindex 18\n'
            '        wdev 0x2\n'
            '        addr 63:85:a6:21:68:01\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iw_device(raw_data)
        self.assertEqual(str(ctx.exception), 'Missing header')

    def test_invalid_header(self):
        raw_data = (
            'Invalid wlan0\n'
            '        ifindex 18\n'
            '        wdev 0x2\n'
            '        addr 63:85:a6:21:68:01\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iw_device(raw_data)
        self.assertEqual(str(ctx.exception), 'Missing header')

    def test_duplicate_device(self):
        raw_data = (
            'Interface wlan0\n'
            '        ifindex 18\n'
            '        wdev 0x2\n'
            '        addr 63:85:a6:21:68:01\n'
            'Interface wlan0\n'
            '        ifindex 17\n'
            '        wdev 0x100000002\n'
            '        addr ce:91:1c:58:d5:0c\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iw_device(raw_data)
        self.assertEqual(str(ctx.exception), 'Duplicate device')
