from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


MAX_REASSEMBLED_BYTES = 1024 * 1024


@dataclass(frozen=True)
class NetworkDetection:
    verdict: str
    reason_codes: tuple[str, ...]


def detect_proftpd_modcopy(payloads: Iterable[bytes], *, complete: bool) -> NetworkDetection:
    if not complete:
        return NetworkDetection("NOT_EVALUABLE", ("EPR-NET-MISSING-STREAM",))
    stream = bytearray()
    for payload in payloads:
        if len(stream) + len(payload) > MAX_REASSEMBLED_BYTES:
            return NetworkDetection("NOT_EVALUABLE", ("EPR-NET-STREAM-LIMIT",))
        stream.extend(payload)
    cpfr = b"SITE CPFR /proc/self/cmdline" in stream
    cpto = b"SITE CPTO /var/www/" in stream
    if cpfr and cpto:
        return NetworkDetection("SUSPICIOUS", ("EPR-NET-PROFTPD-MODCOPY",))
    return NetworkDetection("BENIGN", ())
