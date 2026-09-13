import unittest
from pathlib import Path

from avr.correlation import evaluate
from avr.evidence import Verdict
from avr.normalization import load_lines


ROOT = Path(__file__).parents[1]


def decision(name: str):
    path = ROOT / "experiments" / "evidence" / f"{name}.ndjson"
    with path.open(encoding="utf-8") as stream:
        return evaluate(load_lines(stream), name)


class RecordedEvidenceTests(unittest.TestCase):
    def test_exp011_is_correlated(self) -> None:
        result = decision("EXP-011")
        self.assertEqual(result.verdict, Verdict.CONFIRMED_ATTACK)
        self.assertEqual(result.telemetry_planes, ("endpoint", "network"))

    def test_benign001_does_not_trigger(self) -> None:
        self.assertEqual(decision("BENIGN-001").verdict, Verdict.BENIGN)


if __name__ == "__main__":
    unittest.main()
