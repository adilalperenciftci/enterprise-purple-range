import struct
import tempfile
import unittest
from pathlib import Path

from avr.pcap import PcapError, flows


def capture(packet: bytes) -> bytes:
    header = b"\xd4\xc3\xb2\xa1" + struct.pack("<HHiiii", 2, 4, 0, 0, 65535, 1)
    record = struct.pack("<IIII", 1, 0, len(packet), len(packet)) + packet
    return header + record


class PcapTests(unittest.TestCase):
    def test_extracts_ipv4_tcp_flow(self) -> None:
        ethernet = b"\0" * 12 + b"\x08\x00"
        ip = b"\x45\0\0\x28\0\0\0\0\x40\x06\0\0" + bytes([10, 88, 0, 20, 10, 88, 0, 10])
        tcp = struct.pack("!HH", 49152, 53) + b"\0" * 16
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.pcap"
            path.write_bytes(capture(ethernet + ip + tcp))
            self.assertEqual((flows(path)[0].destination_ip, flows(path)[0].destination_port), ("10.88.0.10", 53))

    def test_truncated_capture_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.pcap"
            path.write_bytes(b"\xd4\xc3\xb2\xa1" + b"\0" * 21)
            with self.assertRaises(PcapError):
                flows(path)


if __name__ == "__main__":
    unittest.main()
