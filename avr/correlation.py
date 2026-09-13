from __future__ import annotations

from collections import defaultdict

from .evidence import Decision, EvidenceGraph, Verdict


REQUIRED_PLANES = frozenset({"endpoint", "network"})


def evaluate(graph: EvidenceGraph, experiment_id: str) -> Decision:
    events = tuple(event for event in graph.ordered() if event.experiment_id == experiment_id)
    if not events:
        return Decision(Verdict.NOT_EVALUABLE, ("EPR-NO-EVIDENCE",), (), (), "No evidence was supplied.")
    planes = frozenset(event.plane for event in events)
    ids = tuple(event.event_id for event in events)
    if not REQUIRED_PLANES.issubset(planes):
        return Decision(
            Verdict.INCOMPLETE,
            ("EPR-MISSING-TELEMETRY-PLANE",),
            ids,
            tuple(sorted(planes)),
            "Required endpoint or network evidence is missing.",
        )
    by_source: dict[object, set[str]] = defaultdict(set)
    for event in events:
        if event.source is not None:
            by_source[event.source].add(event.kind)
    correlated = [
        source
        for source, kinds in by_source.items()
        if {"process_create", "network_connection", "marker_write"}.issubset(kinds)
    ]
    if correlated:
        supporting = tuple(
            event.event_id
            for event in events
            if event.source in correlated
            and event.kind in {"process_create", "network_connection", "marker_write"}
        )
        return Decision(
            Verdict.CONFIRMED_ATTACK,
            ("EPR-PROCESS-NETWORK-MARKER",),
            supporting,
            tuple(sorted(planes)),
            "One process lifetime is supported by execution, connection, and marker evidence.",
        )
    suspicious = tuple(event.event_id for event in events if event.kind in {"network_connection", "marker_write"})
    if suspicious:
        return Decision(
            Verdict.SUSPICIOUS,
            ("EPR-PARTIAL-CORRELATION",),
            suspicious,
            tuple(sorted(planes)),
            "Behavioral evidence exists but cannot be attributed across all required signals.",
        )
    return Decision(
        Verdict.BENIGN,
        ("EPR-BASELINE-ONLY",),
        ids,
        tuple(sorted(planes)),
        "Complete telemetry contains only the declared baseline behavior.",
    )
