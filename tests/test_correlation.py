import random
import unittest

from avr.correlation import evaluate
from avr.evidence import Evidence, EvidenceGraph, ProcessIdentity, Verdict


PROCESS = ProcessIdentity("WIN11", "{11111111-1111-1111-1111-111111111111}", 4242, "2026-09-13T01:00:00Z")


def event(number: int, kind: str, plane: str, process: ProcessIdentity | None = PROCESS) -> Evidence:
    return Evidence.create(event_id=f"e{number}", experiment_id="EXP-011", timestamp_utc=f"2026-09-13T01:00:{number:02d}Z", plane=plane, kind=kind, source=process)


ATTACK = (
    event(1, "process_create", "endpoint"),
    event(2, "network_connection", "network"),
    event(3, "marker_write", "endpoint"),
)


class CorrelationTests(unittest.TestCase):
    def graph(self, events=ATTACK) -> EvidenceGraph:
        graph = EvidenceGraph()
        for item in events:
            graph.add(item)
        return graph

    def test_multiplane_attack_is_confirmed(self) -> None:
        decision = evaluate(self.graph(), "EXP-011")
        self.assertEqual(decision.verdict, Verdict.CONFIRMED_ATTACK)
        self.assertEqual(set(decision.telemetry_planes), {"endpoint", "network"})

    def test_missing_plane_is_incomplete(self) -> None:
        self.assertEqual(evaluate(self.graph(ATTACK[:1]), "EXP-011").verdict, Verdict.INCOMPLETE)

    def test_duplicate_does_not_increase_evidence(self) -> None:
        graph = self.graph()
        graph.add(ATTACK[1])
        self.assertEqual(len(evaluate(graph, "EXP-011").evidence_ids), 3)

    def test_reordering_preserves_decision(self) -> None:
        expected = evaluate(self.graph(), "EXP-011")
        for seed in range(30):
            shuffled = list(ATTACK)
            random.Random(seed).shuffle(shuffled)
            self.assertEqual(evaluate(self.graph(shuffled), "EXP-011"), expected)

    def test_pid_reuse_does_not_merge_lifetimes(self) -> None:
        reused = ProcessIdentity("WIN11", "{22222222-2222-2222-2222-222222222222}", 4242, "2026-09-13T02:00:00Z")
        events = (ATTACK[0], ATTACK[1], event(3, "marker_write", "endpoint", reused))
        self.assertEqual(evaluate(self.graph(events), "EXP-011").verdict, Verdict.SUSPICIOUS)

    def test_remove_evidence_never_increases_trust(self) -> None:
        rank = {Verdict.NOT_EVALUABLE: 0, Verdict.INCOMPLETE: 0, Verdict.SUSPICIOUS: 1, Verdict.CONFIRMED_ATTACK: 2, Verdict.BENIGN: 2}
        complete = evaluate(self.graph(), "EXP-011")
        for index in range(len(ATTACK)):
            reduced = ATTACK[:index] + ATTACK[index + 1 :]
            self.assertLessEqual(rank[evaluate(self.graph(reduced), "EXP-011").verdict], rank[complete.verdict])

    def test_identity_validation(self) -> None:
        with self.assertRaises(ValueError):
            ProcessIdentity("WIN11", "", 4242, "2026-09-13T01:00:00Z")

    def test_contradictory_duplicate_fails(self) -> None:
        graph = self.graph((ATTACK[0],))
        with self.assertRaises(ValueError):
            graph.add(event(1, "marker_write", "endpoint"))

    def test_no_evidence_is_not_evaluable(self) -> None:
        self.assertEqual(evaluate(EvidenceGraph(), "EXP-011").verdict, Verdict.NOT_EVALUABLE)

    def test_credential_auth_execution_requires_three_planes(self) -> None:
        events = tuple(
            Evidence.create(
                event_id=f"c{index}", experiment_id="EXP-018",
                timestamp_utc=f"2026-09-13T03:01:0{index}Z", plane=plane,
                kind=kind, attributes={"credential_id": "SYNTH-SVC-REMOTE"},
            )
            for index, (plane, kind) in enumerate((
                ("endpoint", "credential_access"), ("identity", "authentication"),
                ("network", "network_connection"), ("endpoint", "target_process")), 1)
        )
        self.assertEqual(
            evaluate(self.graph(events), "EXP-018", "credential_auth_execution").verdict,
            Verdict.CONFIRMED_ATTACK,
        )
        self.assertEqual(
            evaluate(self.graph((events[0], events[1], events[3])), "EXP-018", "credential_auth_execution").verdict,
            Verdict.INCOMPLETE,
        )

    def test_auth_transition_rejects_mismatched_join_ids(self) -> None:
        events = tuple(
            Evidence.create(
                event_id=f"t{index}", experiment_id="EXP-018",
                timestamp_utc=f"2026-09-13T03:02:0{index}Z", plane=plane,
                kind=kind, attributes={"transition_id": transition},
            )
            for index, (plane, kind, transition) in enumerate((
                ("identity", "authentication", "A"),
                ("network", "network_connection", "A"),
                ("endpoint", "target_process", "B")), 1)
        )
        self.assertEqual(
            evaluate(self.graph(events), "EXP-018", "auth_host_transition").verdict,
            Verdict.SUSPICIOUS,
        )


if __name__ == "__main__":
    unittest.main()
