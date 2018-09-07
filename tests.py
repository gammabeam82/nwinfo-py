import unittest
import nwinfo


class TestNW(unittest.TestCase):

    def setUp(self):
        self.nmap_output = """
        Nmap scan report for 192.168.1.1
        Host is up (0.00057s latency).
        MAC Address: 54:22:F8:FF:FF:FF (zte)
        Nmap scan report for 192.168.1.2
        Host is up (0.082s latency).
        MAC Address: 50:8F:4C:FF:FF:FF (Unknown)
        Nmap scan report for 192.168.1.6
        Host is up.
        Nmap done: 64 IP addresses (3 hosts up) scanned in 4.57 seconds
        """
        self.nw = nwinfo.Network()

    def test_parse(self):
        parsed = {
            ('192.168.1.1', '54:22:F8:FF:FF:FF'),
            ('192.168.1.6', ''),
            ('192.168.1.2', '50:8F:4C:FF:FF:FF')
        }

        self.assertEqual(self.nw.parse(self.nmap_output), parsed)


if __name__ == '__main__':
    unittest.main()
