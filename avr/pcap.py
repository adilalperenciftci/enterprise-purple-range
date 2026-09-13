from __future__ import annotations

import ipaddress
import struct
from dataclasses import dataclass
from pathlib import Path


MAX_CAPTURE_BYTES = 64 * 1024 * 1024


class PcapError(ValueError):
    pass


@dataclass(frozen=True)
class Flow:
    source_ip: str
    destination_ip: str
    source_port: int
    destination_port: int
    protocol: str


def flows(path: Path) -> tuple[Flow, ...]:
    size = path.stat().st_size
    if size < 24 or size > MAX_CAPTURE_BYTES:
        raise PcapError("capture size is invalid")
    data = path.read_bytes()
    magic = data[:4]
    if magic == b"\xd4\xc3\xb2\xa1":
        endian = "<"
    elif magic == b"\xa1\xb2\xc3\xd4":
        endian = ">"
    else:
        raise PcapError("unsupported capture format")
    _, _, _, _, _, linktype = struct.unpack_from(endian + "HHiiii", data, 4)
    if linktype != 1:
        raise PcapError("only Ethernet captures are supported")
    offset = 24
    found: set[Flow] = set()
    while offset < len(data):
        if len(data) - offset < 16:
            raise PcapError("truncated packet header")
        _, _, captured, original = struct.unpack_from(endian + "IIII", data, offset)
        offset += 16
        if captured > original or captured > 262_144 or offset + captured > len(data):
            raise PcapError("invalid packet length")
        packet = data[offset:offset + captured]
        offset += captured
        if len(packet) < 38 or packet[12:14] != b"\x08\x00":
            continue
        ihl = (packet[14] & 0x0F) * 4
        protocol = packet[23]
        transport = 14 + ihl
        if ihl < 20 or len(packet) < transport + 4 or protocol not in (6, 17):
            continue
        source_port, destination_port = struct.unpack_from("!HH", packet, transport)
        found.add(Flow(
            str(ipaddress.ip_address(packet[26:30])),
            str(ipaddress.ip_address(packet[30:34])),
            source_port,
            destination_port,
            "tcp" if protocol == 6 else "udp",
        ))
    return tuple(sorted(found, key=lambda flow: (
        flow.source_ip, flow.destination_ip, flow.source_port, flow.destination_port, flow.protocol
    )))
