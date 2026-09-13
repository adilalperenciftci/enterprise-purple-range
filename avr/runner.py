from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .authorization import AuthorizationError, RangeManifest
from .topology import VMRequirement, parse_machine_readable, validate_vm


ROOT = Path(__file__).parents[1]
VBOX = Path(os.environ.get("VBOX_MSI_INSTALL_PATH", r"C:\Program Files\Oracle\VirtualBox")) / "VBoxManage.exe"


@dataclass(frozen=True)
class Experiment:
    source: str
    target: str
    vm: VMRequirement
    executable: str
    arguments: tuple[str, ...]
    target_vm: VMRequirement | None = None


EXPERIMENTS = {
    "EXP-005": Experiment(
        "WIN11",
        "WIN11",
        VMRequirement("EPR-WIN11", "080027880020"),
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        ("-NoProfile", "-NonInteractive", "-File", r"C:\AVR-Lab\Experiments\EXP-005.ps1"),
    ),
    "BENIGN-001": Experiment(
        "WIN11",
        "WIN11",
        VMRequirement("EPR-WIN11", "080027880020"),
        r"C:\Windows\System32\whoami.exe",
        (),
    ),
    "EXP-011": Experiment(
        "WIN11",
        "DC01",
        VMRequirement("EPR-WIN11", "080027880020"),
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        ("-NoProfile", "-NonInteractive", "-File", r"C:\AVR-Lab\Experiments\EXP-011.ps1"),
        VMRequirement("EPR-DC01", "080027880010"),
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


def prepare(experiment_id: str, target_ip: str) -> tuple[Experiment, Path]:
    try:
        experiment = EXPERIMENTS[experiment_id]
    except KeyError as exc:
        raise AuthorizationError("unknown experiment") from exc
    manifest = RangeManifest.load(ROOT / "range" / "manifest.json")
    manifest.authorize(experiment.source, experiment.target, target_ip)
    validate_vm(_show_vm(experiment.vm.name), experiment.vm)
    if experiment.target_vm is not None:
        validate_vm(_show_vm(experiment.target_vm.name), experiment.target_vm)
    secret = ROOT / "secrets" / "win11-password.txt"
    if not secret.is_file():
        raise AuthorizationError("lab password file is unavailable")
    return experiment, secret


def execute(experiment_id: str, target_ip: str) -> int:
    experiment, secret = prepare(experiment_id, target_ip)
    command = [
        str(VBOX), "guestcontrol", experiment.vm.name, "run", "--username", "lablocal",
        "--passwordfile", str(secret), "--exe", experiment.executable, "--",
        experiment.executable, *experiment.arguments,
    ]
    return subprocess.run(command, check=False, timeout=120).returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", choices=tuple(EXPERIMENTS))
    parser.add_argument("target_ip")
    args = parser.parse_args()
    try:
        return execute(args.experiment, args.target_ip)
    except AuthorizationError as exc:
        print(json.dumps({"status": "ABORT", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
