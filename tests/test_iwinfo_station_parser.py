import unittest

from apparse import parse_iwinfo_station


class TestIwinfoStationParser(unittest.TestCase):

    def test_valid(self):
        raw_data = (
            '90:44:59:4A:44:B2  -51 dBm / -106 dBm (SNR 55)  21 ms ago\n'
            '        RX: 6.8 MBit/s                                   488 Pkts.\n'
            '        TX: 156.8 MBit/s, VHT-MCS 3, 80MHz, VHT-NSS 1      5708 Pkts.\n'
            '        expected throughput: unknown\n\n'
            'F4:1A:29:64:55:5A  -53 dBm / -98 dBm (SNR 45)  372 ms ago\n'
            '        RX: 124.2 MBit/s, MCS 7, 20MHz                  3413 Pkts.\n'
            '        TX: 183.5 MBit/s, MCS 6, 20MHz                  9856 Pkts.\n'
            '        expected throughput: 148.9 MBit/s\n'
        )
        expected_data = {
            '90:44:59:4A:44:B2': {
                'signal': -51,
                'noise': -106,
                'snr': 55,
                'inactive_time': 21,
                'rx_rate': 6.8,
                'tx_rate': 156.8,
                'throughput': None,
                'rx_packets': 488,
                'tx_packets': 5708
            },
            'F4:1A:29:64:55:5A': {
                'signal': -53,
                'noise': -98,
                'snr': 45,
                'inactive_time': 372,
                'rx_rate': 124.2,
                'tx_rate': 183.5,
                'throughput': 148.9,
                'rx_packets': 3413,
                'tx_packets': 9856
            }
        }
        parsed_data = parse_iwinfo_station(raw_data)
        self.assertEqual(parsed_data, expected_data)

    def test_invalid(self):
        raw_data = (
            '90:44:59:4A:44:B2  -51 dBm / -106 dBm (SNR 55)  21 ms ago\n'
            '        RX: 6 MBit/s                                   - Pkts.\n'
            '        TX: Invalid MBit/s, VHT-MCS 3, 80MHz, VHT-NSS 1      5708 Pkts.\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iwinfo_station(raw_data)
        self.assertEqual(str(ctx.exception), "Invalid value for key 'RX'")

    def test_missing_header(self):
        raw_data = (
            '        RX: 6.8 MBit/s                                   488 Pkts.\n'
            '        TX: 156.8 MBit/s, VHT-MCS 3, 80MHz, VHT-NSS 1      5708 Pkts.\n'
            '        expected throughput: unknown\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iwinfo_station(raw_data)
        self.assertEqual(str(ctx.exception), 'Missing header')

    def test_invalid_header(self):
        raw_data = (
            '90:44:59:4A:44:B2  0 dBm / Invalid dBm (SNR -)  21 ms ago\n'
            '        RX: 6.8 MBit/s                                   488 Pkts.\n'
            '        TX: 156.8 MBit/s, VHT-MCS 3, 80MHz, VHT-NSS 1      5708 Pkts.\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iwinfo_station(raw_data)
        self.assertEqual(str(ctx.exception), 'Invalid header')

    def test_duplicate_station(self):
        raw_data = (
            '90:44:59:4A:44:B2  -51 dBm / -106 dBm (SNR 55)  21 ms ago\n'
            '        RX: 6.8 MBit/s                                   488 Pkts.\n'
            '        TX: 156.8 MBit/s, VHT-MCS 3, 80MHz, VHT-NSS 1      5708 Pkts.\n\n'
            '90:44:59:4A:44:B2  -51 dBm / -106 dBm (SNR 55)  21 ms ago\n'
            '        RX: 124.2 MBit/s, MCS 7, 20MHz                  3413 Pkts.\n'
            '        TX: 183.5 MBit/s, MCS 6, 20MHz                  9856 Pkts.\n'
        )
        with self.assertRaises(ValueError) as ctx:
            parse_iwinfo_station(raw_data)
        self.assertEqual(str(ctx.exception), 'Duplicate station')
