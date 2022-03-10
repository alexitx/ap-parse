import unittest

from apparse import parse_iwinfo_device


class TestIwinfoDeviceParser(unittest.TestCase):

    def test_valid(self):
        raw_data = (
            'wlan0     ESSID: "Access Point 5GHz SSID"\n'
            '          Access Point: 63:85:A6:21:68:01\n'
            '          Mode: Master  Channel: 44 (5.220 GHz)\n'
            '          Tx-Power: 23 dBm  Link Quality: 58/70\n'
            '          Signal: -52 dBm  Noise: -105 dBm\n'
            '          Bit Rate: 127.2 MBit/s\n'
            '          Encryption: WPA2 PSK (CCMP)\n'
            '          Type: nl80211  HW Mode(s): 802.11nac\n'
            '          Hardware: 36FD:454C D2F3:DB5D [Qualcomm Atheros QCA9880]\n'
            '          TX power offset: none\n'
            '          Frequency offset: none\n'
            '          Supports VAPs: yes  PHY name: phy0\n\n'
            'wlan1     ESSID: "Access Point 2.4GHz SSID"\n'
            '          Access Point: CE:91:1C:58:D5:0C\n'
            '          Mode: Master  Channel: 10 (2.457 GHz)\n'
            '          Tx-Power: 17 dBm  Link Quality: 54/70\n'
            '          Signal: -56 dBm  Noise: -95 dBm\n'
            '          Bit Rate: 95.6 MBit/s\n'
            '          Encryption: WPA2 PSK (CCMP)\n'
            '          Type: nl80211  HW Mode(s): 802.11bgn\n'
            '          Hardware: unknown [Generic MAC80211]\n'
            '          TX power offset: unknown\n'
            '          Frequency offset: unknown\n'
            '          Supports VAPs: yes  PHY name: phy1\n'
        )
        expected_data = {
            'wlan0': {
                'ssid': 'Access Point 5GHz SSID',
                'mac_address': '63:85:A6:21:68:01',
                'mode': 'Master',
                'channel': 44,
                'frequency': 5220,
                'tx_power': 23,
                'quality': 82,
                'signal': -52,
                'noise': -105,
                'bitrate': 127.2,
                'encryption': 'WPA2 PSK (CCMP)',
                'type': 'nl80211',
                'modes': '802.11nac',
                'hardware_id': '36FD:454C D2F3:DB5D',
                'hardware_name': 'Qualcomm Atheros QCA9880',
                'vap_support': True,
                'phy_name': 'phy0'
            },
            'wlan1': {
                'ssid': 'Access Point 2.4GHz SSID',
                'mac_address': 'CE:91:1C:58:D5:0C',
                'mode': 'Master',
                'channel': 10,
                'frequency': 2457,
                'tx_power': 17,
                'quality': 77,
                'signal': -56,
                'noise': -95,
                'bitrate': 95.6,
                'encryption': 'WPA2 PSK (CCMP)',
                'type': 'nl80211',
                'modes': '802.11bgn',
                'hardware_id': None,
                'hardware_name': 'Generic MAC80211',
                'vap_support': True,
                'phy_name': 'phy1'
            }
        }
        parsed_data = parse_iwinfo_device(raw_data)
        self.assertEqual(parsed_data, expected_data)

    def test_invalid(self):
        raw_data = (
            'wlan0     ESSID: "Access Point 5GHz SSID"\n'
            '          Access Point: 63:85:A6:21:68:01\n'
            '          Mode: Master  Invalid Channel: -44 (5 GHz)\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iwinfo_device(raw_data)
        self.assertEqual(str(ctx.exception), "Invalid value for key 'Mode'")

    def test_missing_header(self):
        raw_data = (
            '          Access Point: 63:85:A6:21:68:01\n'
            '          Mode: Master  Channel: 44 (5.220 GHz)\n'
            '          Tx-Power: 23 dBm  Link Quality: 58/70\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iwinfo_device(raw_data)
        self.assertEqual(str(ctx.exception), 'Missing header')

    def test_invalid_header(self):
        raw_data = (
            'wlan0     Invalid: Access Point 5GHz SSID\n'
            '          Access Point: 63:85:A6:21:68:01\n'
            '          Mode: Master  Channel: 44 (5.220 GHz)\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iwinfo_device(raw_data)
        self.assertEqual(str(ctx.exception), 'Invalid header')

    def test_duplicate_device(self):
        raw_data = (
            'wlan0     ESSID: "Access Point 5GHz SSID"\n'
            '          Access Point: 63:85:A6:21:68:01\n'
            '          Mode: Master  Channel: 44 (5.220 GHz)\n\n'
            'wlan0     ESSID: "Access Point 5GHz SSID"\n'
            '          Access Point: CE:91:1C:58:D5:0C\n'
            '          Mode: Master  Channel: 10 (2.457 GHz)\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iwinfo_device(raw_data)
        self.assertEqual(str(ctx.exception), 'Duplicate device')
