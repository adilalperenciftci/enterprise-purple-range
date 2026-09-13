import unittest

from avr.authorization import AuthorizationError
from avr.topology import VMRequirement, parse_machine_readable, validate_vm


VALID = {
    "name": "EPR-WIN11",
    "VMState": "running",
    "nic1": "intnet",
    "intnet1": "epr-isolated",
    "macaddress1": "080027880020",
    "nic2": "none",
}


class TopologyTests(unittest.TestCase):
    def test_parser(self) -> None:
        self.assertEqual(parse_machine_readable('name="EPR-WIN11"\nnic1="intnet"\n'), {"name": "EPR-WIN11", "nic1": "intnet"})

    def test_expected_identity_and_isolation(self) -> None:
        validate_vm(VALID, VMRequirement("EPR-WIN11", "080027880020"))

    def test_rejects_connected_secondary_adapters(self) -> None:
        for mode in ("nat", "bridged", "hostonly"):
            with self.subTest(mode=mode), self.assertRaises(AuthorizationError):
                validate_vm({**VALID, "nic2": mode}, VMRequirement("EPR-WIN11", "080027880020"))

    def test_rejects_wrong_identity_network_and_state(self) -> None:
        mutations = ({"name": "WIN11"}, {"VMState": "poweroff"}, {"intnet1": "other"}, {"macaddress1": "080027000000"})
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(AuthorizationError):
                validate_vm({**VALID, **mutation}, VMRequirement("EPR-WIN11", "080027880020"))


if __name__ == "__main__":
    unittest.main()

