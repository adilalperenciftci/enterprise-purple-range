from __future__ import annotations

import re
from dataclasses import dataclass

from .authorization import AuthorizationError


EXPECTED_NETWORK = "epr-isolated"


def parse_machine_readable(raw: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in raw.splitlines():
        match = re.fullmatch(r'([^=]+)="(.*)"', line)
        if match:
            values[match.group(1)] = match.group(2)
    return values


@dataclass(frozen=True)
class VMRequirement:
    name: str
    mac: str


def validate_vm(values: dict[str, str], requirement: VMRequirement) -> None:
    if values.get("name") != requirement.name:
        raise AuthorizationError("VM identity mismatch")
    if values.get("VMState") != "running":
        raise AuthorizationError("required VM is not running")
    if values.get("nic1") != "intnet" or values.get("intnet1") != EXPECTED_NETWORK:
        raise AuthorizationError("primary adapter is not on the isolated network")
    if values.get("macaddress1", "").casefold() != requirement.mac.casefold():
        raise AuthorizationError("VM MAC identity mismatch")
    for slot in range(2, 9):
        mode = values.get(f"nic{slot}", "none")
        if mode not in {"none", "null"}:
            raise AuthorizationError(f"adapter {slot} is not disconnected")

