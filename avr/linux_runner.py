from __future__ import annotations

import argparse
import json
import os
import subprocess
import shlex
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
    controller_vm: VMRequirement
    command: str


EXPERIMENTS = {
    "EXP-001": LinuxExperiment(
        "KALI",
        "META",
        VMRequirement("EPR-KALI", "080027880030"),
        VMRequirement("EPR-META", "080027880040", 2),
        VMRequirement("EPR-WIN11", "080027880020"),
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
    validate_vm(_show_vm(experiment.controller_vm.name), experiment.controller_vm)
    secret = ROOT / "secrets" / "labadmin-password.txt"
    if not secret.is_file():
        raise AuthorizationError("controller password file is unavailable")
    return experiment, secret


def execute(experiment_id: str, target_ip: str) -> int:
    experiment, secret = prepare(experiment_id, target_ip)
    command = [
        str(VBOX), "guestcontrol", experiment.controller_vm.name, "run",
        "--username", "labadmin", "--domain", "LAB", "--passwordfile", str(secret),
        "--wait-stdout", "--wait-stderr", "--timeout", "120000",
        "--exe", r"C:\Windows\System32\OpenSSH\ssh.exe", "--",
        "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=NUL", "-i", r"C:\AVR-Lab\Keys\kali_key",
        "vagrant@10.88.0.30", *shlex.split(experiment.command),
    ]
    return subprocess.run(command, check=False, timeout=130).returncode


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
