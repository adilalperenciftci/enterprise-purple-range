import json
import tempfile
import unittest
from pathlib import Path

from avr.authorization import AuthorizationError, RangeManifest
from avr.catalog import validate_catalog
from avr.correlation import PROFILES


ROOT = Path(__file__).parents[1]


class CatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = RangeManifest.load(ROOT / "range" / "manifest.json")
        self.path = ROOT / "range" / "experiment-catalog.json"

    def test_required_catalog_is_valid(self) -> None:
        catalog = validate_catalog(self.path, self.manifest)
        self.assertEqual(len(catalog["experiments"]), 20)
        self.assertEqual(len(catalog["baselines"]), 6)

    def test_unauthorized_pair_fails(self) -> None:
        catalog = json.loads(self.path.read_text(encoding="utf-8"))
        catalog["experiments"][0]["source"] = "META"
        catalog["experiments"][0]["target"] = "DC01"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(json.dumps(catalog), encoding="utf-8")
            with self.assertRaises(AuthorizationError):
                validate_catalog(path, self.manifest)

    def test_correlation_rules_match_engine_profiles(self) -> None:
        rules = ROOT / "detections" / "correlation"
        for path in rules.glob("*.json"):
            rule = json.loads(path.read_text(encoding="utf-8"))
            profile = PROFILES[rule["profile"]]
            self.assertEqual(set(rule["required_planes"]), set(profile.required_planes))
            self.assertEqual(set(rule["required_kinds"]), set(profile.required_kinds))

    def test_atomic_selection_is_pinned_and_unique(self) -> None:
        selection = json.loads((ROOT / "range" / "atomic-selection.json").read_text(encoding="utf-8"))
        self.assertRegex(selection["commit"], r"^[0-9a-f]{40}$")
        guids = [test["guid"] for test in selection["tests"]]
        experiments = [test["experiment"] for test in selection["tests"]]
        self.assertEqual(len(guids), len(set(guids)))
        self.assertEqual(experiments, [f"EXP-{number:03d}" for number in range(5, 11)])


if __name__ == "__main__":
    unittest.main()
