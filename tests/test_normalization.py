import json
import random
import string
import unittest

from avr.normalization import NormalizationError, load_lines, parse_line


VALID = {
    "event_id": "sysmon-1",
    "experiment_id": "EXP-011",
    "timestamp_utc": "2026-09-13T03:30:00Z",
    "plane": "endpoint",
    "kind": "process_create",
    "source": {
        "host": "WIN11",
        "process_guid": "{11111111-1111-1111-1111-111111111111}",
        "pid": 4242,
        "started_utc": "2026-09-13T03:30:00Z",
    },
    "target_host": "WIN11",
    "attributes": {"image": "powershell.exe"},
}


class NormalizationTests(unittest.TestCase):
    def test_valid_event(self) -> None:
        self.assertEqual(parse_line(json.dumps(VALID)).source.pid, 4242)

    def test_unknown_or_missing_fields_fail(self) -> None:
        cases = ({**VALID, "secret": "x"}, {key: value for key, value in VALID.items() if key != "event_id"})
        for case in cases:
            with self.subTest(case=case), self.assertRaises(NormalizationError):
                parse_line(json.dumps(case))

    def test_invalid_process_identity_fails(self) -> None:
        for process in ({**VALID["source"], "pid": 0}, {"pid": 42}, {**VALID["source"], "extra": "x"}):
            with self.subTest(process=process), self.assertRaises(NormalizationError):
                parse_line(json.dumps({**VALID, "source": process}))

    def test_malformed_inputs_fail_closed(self) -> None:
        randomizer = random.Random(8800)
        alphabet = string.printable
        for _ in range(100):
            malformed = "".join(randomizer.choice(alphabet) for _ in range(randomizer.randint(1, 256)))
            with self.assertRaises(NormalizationError):
                parse_line(malformed)

    def test_duplicate_lines_do_not_multiply_events(self) -> None:
        line = json.dumps(VALID)
        self.assertEqual(len(load_lines((line, line)).ordered()), 1)

    def test_oversized_line_fails(self) -> None:
        with self.assertRaises(NormalizationError):
            parse_line("x" * 65_537)


if __name__ == "__main__":
    unittest.main()
