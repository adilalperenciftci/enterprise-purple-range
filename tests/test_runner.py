import unittest
from unittest.mock import patch

from avr.authorization import AuthorizationError
from avr.runner import EXPERIMENTS, prepare


VALID_VM = {
    "name": "EPR-WIN11", "VMState": "running", "nic1": "intnet",
    "intnet1": "epr-isolated", "macaddress1": "080027880020",
}


class RunnerTests(unittest.TestCase):
    def test_fixed_commands_have_no_target_interpolation(self) -> None:
        for experiment in EXPERIMENTS.values():
            self.assertNotIn("{", experiment.executable + "".join(experiment.arguments))

    @patch("avr.runner._show_vm", return_value=VALID_VM)
    def test_external_target_aborts_before_secret_or_execution(self, _show) -> None:
        for target in ("192.0.2.1", "8.8.8.8", "10.88.0.0/24"):
            with self.subTest(target=target), self.assertRaises(AuthorizationError):
                prepare("EXP-005", target)

    def test_unknown_experiment_aborts(self) -> None:
        with self.assertRaises(AuthorizationError):
            prepare("EXP-999", "10.88.0.20")


if __name__ == "__main__":
    unittest.main()

