import json
import tempfile
import unittest
from pathlib import Path

from avr.authorization import AuthorizationError, RangeManifest


ROOT = Path(__file__).parents[1]


class AuthorizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = RangeManifest.load(ROOT / "range" / "manifest.json")

    def test_approved_pair_and_exact_ip(self) -> None:
        self.assertEqual(self.manifest.authorize("KALI", "WIN11", "10.88.0.20").name, "WIN11")

    def test_rejects_external_and_target_expressions(self) -> None:
        for target in ("192.0.2.1", "198.51.100.1", "127.0.0.1", "8.8.8.8", "1.1.1.1", "0.0.0.0/0", "10.88.0.0/24", "win11", "10.88.0.20,10.88.0.10"):
            with self.subTest(target=target), self.assertRaises(AuthorizationError):
                self.manifest.authorize("KALI", "WIN11", target)

    def test_rejects_unauthorized_pair(self) -> None:
        with self.assertRaises(AuthorizationError):
            self.manifest.authorize("META", "DC01", "10.88.0.10")

    def test_synthetic_credential_boundary(self) -> None:
        self.manifest.authorize_credential_path(r"C:\AVR-Lab\Synthetic\svc_web.json")
        for path in (r"C:\Users\Example\.ssh\id_rsa", r"C:\AVR-Lab\Synthetic-Evil\x"):
            with self.subTest(path=path), self.assertRaises(AuthorizationError):
                self.manifest.authorize_credential_path(path)

    def test_duplicate_manifest_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text('{"network":"10.88.0.0/24","network":"10.0.0.0/24"}', encoding="utf-8")
            with self.assertRaises(AuthorizationError):
                RangeManifest.load(path)


if __name__ == "__main__":
    unittest.main()
