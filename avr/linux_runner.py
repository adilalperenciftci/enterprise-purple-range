from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .authorization import AuthorizationError, RangeManifest
from .topology import VMRequirement, parse_machine_readable, validate_vm


ROOT = Path(__file__).parents[1]
VBOX = Path(os.environ.get("VBOX_MSI_INSTALL_PATH", r"C:\Program Files\Oracle\VirtualBox")) / "VBoxManage.exe"


@dataclass(frozen=True)
class LinuxExperiment:
    source: str
    target: str
    source_vm: VMRequirement
    target_vm: VMRequirement
    command: str


EXPERIMENTS = {
    "EXP-001": LinuxExperiment(
        "KALI",
        "META",
        VMRequirement("EPR-KALI", "080027880030"),
        VMRequirement("EPR-META", "080027880040", 2),
        "nmap -Pn -n -sT -sV --version-light --top-ports 100 10.88.0.40 -oN /tmp/epr-exp001.txt",
    ),
}


def _show_vm(name: str) -> dict[str, str]:
    result = subprocess.run(
        [str(VBOX), "showvminfo", name, "--machinereadable"],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode:
        raise AuthorizationError("unable to read VM state")
    return parse_machine_readable(result.stdout)


def prepare(experiment_id: str, target_ip: str) -> tuple[LinuxExperiment, Path]:
    try:
        experiment = EXPERIMENTS[experiment_id]
    except KeyError as exc:
        raise AuthorizationError("unknown Linux experiment") from exc
    manifest = RangeManifest.load(ROOT / "range" / "manifest.json")
    manifest.authorize(experiment.source, experiment.target, target_ip)
    validate_vm(_show_vm(experiment.source_vm.name), experiment.source_vm)
    validate_vm(_show_vm(experiment.target_vm.name), experiment.target_vm)
    secret = ROOT / "secrets" / "kali-password.txt"
    if not secret.is_file():
        raise AuthorizationError("Kali lab password file is unavailable")
    return experiment, secret


def _control(*arguments: str) -> None:
    result = subprocess.run([str(VBOX), "controlvm", "EPR-KALI", *arguments], check=False, timeout=15)
    if result.returncode:
        raise RuntimeError("VirtualBox console input failed")


def execute(experiment_id: str, target_ip: str) -> int:
    experiment, secret = prepare(experiment_id, target_ip)
    password = secret.read_text(encoding="utf-8").strip()
    if not password or any(character.isspace() for character in password):
        raise AuthorizationError("Kali lab password is malformed")

    _control("keyboardputscancode", "1d", "38", "3d", "bd", "b8", "9d")
    time.sleep(2)
    _control("keyboardputscancode", "1c", "9c")
    time.sleep(1)
    _control("keyboardputstring", "vagrant")
    time.sleep(1)
    _control("keyboardputscancode", "1c", "9c")
    time.sleep(1)
    _control("keyboardputstring", password)
    time.sleep(1)
    _control("keyboardputscancode", "1c", "9c")
    time.sleep(2)
    _control("keyboardputstring", experiment.command)
    time.sleep(1)
    _control("keyboardputscancode", "1c", "9c")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", choices=tuple(EXPERIMENTS))
    parser.add_argument("target_ip")
    args = parser.parse_args()
    try:
        return execute(args.experiment, args.target_ip)
    except (AuthorizationError, RuntimeError) as exc:
        print(json.dumps({"status": "ABORT", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
