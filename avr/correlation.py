from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .evidence import Decision, EvidenceGraph, Verdict


@dataclass(frozen=True)
class CorrelationProfile:
    reason: str
    required_planes: frozenset[str]
    required_kinds: frozenset[str]
    trigger_kinds: frozenset[str]
    join_attribute: str | None = None


PROFILES = {
    "process_network_marker": CorrelationProfile(
        "EPR-PROCESS-NETWORK-MARKER",
        frozenset({"endpoint", "network"}),
        frozenset({"process_create", "network_connection", "marker_write"}),
        frozenset({"marker_write"}),
    ),
    "credential_auth_execution": CorrelationProfile(
        "EPR-CREDENTIAL-AUTH-EXECUTION",
        frozenset({"endpoint", "identity", "network"}),
        frozenset({"credential_access", "authentication", "network_connection", "target_process"}),
        frozenset({"credential_access"}),
        "credential_id",
    ),
    "auth_host_transition": CorrelationProfile(
        "EPR-AUTH-HOST-TRANSITION",
        frozenset({"endpoint", "identity", "network"}),
        frozenset({"authentication", "network_connection", "target_process"}),
        frozenset({"authentication", "target_process"}),
        "transition_id",
    ),
}


def evaluate(
    graph: EvidenceGraph,
    experiment_id: str,
    profile_name: str = "process_network_marker",
) -> Decision:
    try:
        profile = PROFILES[profile_name]
    except KeyError as exc:
        raise ValueError("unknown correlation profile") from exc
    events = tuple(event for event in graph.ordered() if event.experiment_id == experiment_id)
    if not events:
        return Decision(Verdict.NOT_EVALUABLE, ("EPR-NO-EVIDENCE",), (), (), "No evidence was supplied.")
    planes = frozenset(event.plane for event in events)
    ids = tuple(event.event_id for event in events)
    if not profile.required_planes.issubset(planes):
        return Decision(
            Verdict.INCOMPLETE,
            ("EPR-MISSING-TELEMETRY-PLANE",),
            ids,
            tuple(sorted(planes)),
            "Required endpoint or network evidence is missing.",
        )
    grouped: dict[object, set[str]] = defaultdict(set)
    if profile.join_attribute is None:
        for event in events:
            if event.source is not None:
                grouped[event.source].add(event.kind)
    else:
        for event in events:
            attributes = dict(event.attributes)
            value = attributes.get(profile.join_attribute)
            if value:
                grouped[value].add(event.kind)
    correlated = [key for key, kinds in grouped.items() if profile.required_kinds.issubset(kinds)]
    if correlated:
        supporting = tuple(
            event.event_id
            for event in events
            if event.kind in profile.required_kinds
            and (
                event.source in correlated
                if profile.join_attribute is None
                else dict(event.attributes).get(profile.join_attribute) in correlated
            )
        )
        return Decision(
            Verdict.CONFIRMED_ATTACK,
            (profile.reason,),
            supporting,
            tuple(sorted(planes)),
            "Independent required telemetry planes correlate on one stable evidence key.",
        )
    triggered = any(event.kind in profile.trigger_kinds for event in events)
    suspicious = tuple(event.event_id for event in events if event.kind in profile.required_kinds) if triggered else ()
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
