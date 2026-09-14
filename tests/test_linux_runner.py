import unittest
from unittest.mock import patch

from avr.authorization import AuthorizationError
from avr.linux_runner import EXPERIMENTS, prepare


KALI = {
    "name": "EPR-KALI", "VMState": "running", "nic1": "intnet",
    "intnet1": "epr-isolated", "macaddress1": "080027880030", "nic2": "none",
}
META = {
    "name": "EPR-META", "VMState": "running", "nic1": "null", "nic2": "intnet",
    "intnet2": "epr-isolated", "macaddress2": "080027880040",
}


class LinuxRunnerTests(unittest.TestCase):
    def test_command_is_fixed_to_literal_manifest_target(self) -> None:
        command = EXPERIMENTS["EXP-001"].command
        self.assertIn("10.88.0.40", command)
        self.assertNotIn("{", command)
        self.assertNotIn("/24", command)

    @patch("pathlib.Path.is_file", return_value=True)
    @patch("avr.linux_runner._show_vm", side_effect=[KALI, META])
    def test_valid_pair_checks_both_live_vms(self, show_vm, _is_file) -> None:
        experiment, _ = prepare("EXP-001", "10.88.0.40")
        self.assertEqual(experiment.source, "KALI")
        self.assertEqual([call.args[0] for call in show_vm.call_args_list], ["EPR-KALI", "EPR-META"])

    def test_nonliteral_and_external_targets_fail_before_vm_access(self) -> None:
        for target in ("10.88.0.0/24", "192.0.2.1", "8.8.8.8", "META"):
            with self.subTest(target=target), self.assertRaises(AuthorizationError):
                prepare("EXP-001", target)


if __name__ == "__main__":
    unittest.main()
