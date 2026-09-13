from __future__ import annotations

import ipaddress
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class AuthorizationError(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AuthorizationError(f"duplicate manifest key: {key}")
        result[key] = value
    return result


@dataclass(frozen=True)
class Host:
    name: str
    ip: ipaddress.IPv4Address
    role: str


@dataclass(frozen=True)
class RangeManifest:
    network: ipaddress.IPv4Network
    hosts: dict[str, Host]
    approved_pairs: frozenset[tuple[str, str]]
    credential_roots: tuple[str, ...]

    @classmethod
    def load(cls, path: Path) -> "RangeManifest":
        raw = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
        try:
            network = ipaddress.ip_network(raw["network"], strict=True)
            if not isinstance(network, ipaddress.IPv4Network) or network.prefixlen != 24:
                raise AuthorizationError("the isolated network must be one exact IPv4 /24")
            hosts = {
                name: Host(name, ipaddress.ip_address(item["ip"]), item["role"])
                for name, item in raw["hosts"].items()
            }
            pairs = frozenset(tuple(pair) for pair in raw["approved_pairs"])
            roots = tuple(raw["synthetic_credential_roots"])
        except (KeyError, TypeError, ValueError) as exc:
            raise AuthorizationError("invalid range manifest") from exc
        if len({host.ip for host in hosts.values()}) != len(hosts):
            raise AuthorizationError("host addresses must be unique")
        if any(host.ip not in network for host in hosts.values()):
            raise AuthorizationError("every host must belong to the isolated network")
        if any(len(pair) != 2 or pair[0] not in hosts or pair[1] not in hosts for pair in pairs):
            raise AuthorizationError("approved pair references an unknown host")
        return cls(network, hosts, pairs, roots)

    def authorize(self, source: str, target: str, literal_ip: str) -> Host:
        if any(marker in literal_ip for marker in ("/", ",", "*")):
            raise AuthorizationError("target expressions are forbidden")
        try:
            address = ipaddress.ip_address(literal_ip)
        except ValueError as exc:
            raise AuthorizationError("target must be a literal IPv4 address") from exc
        if not isinstance(address, ipaddress.IPv4Address):
            raise AuthorizationError("target must be IPv4")
        if (source, target) not in self.approved_pairs:
            raise AuthorizationError("source/target pair is not approved")
        host = self.hosts[target]
        if address != host.ip or address not in self.network:
            raise AuthorizationError("target does not match the approved host")
        return host

    def authorize_credential_path(self, path: str) -> None:
        normalized = path.replace("/", "\\").casefold().rstrip("\\")
        roots = tuple(root.replace("/", "\\").casefold().rstrip("\\") for root in self.credential_roots)
        if not any(normalized == root or normalized.startswith(root + "\\") for root in roots):
            raise AuthorizationError("credential source is outside a synthetic root")
