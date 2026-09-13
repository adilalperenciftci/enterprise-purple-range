from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Verdict(StrEnum):
    BENIGN = "BENIGN"
    SUSPICIOUS = "SUSPICIOUS"
    CONFIRMED_ATTACK = "CONFIRMED_ATTACK"
    INCOMPLETE = "INCOMPLETE"
    NOT_EVALUABLE = "NOT_EVALUABLE"


@dataclass(frozen=True, order=True)
class ProcessIdentity:
    host: str
    process_guid: str
    pid: int
    started_utc: str

    def __post_init__(self) -> None:
        if not self.process_guid or self.pid <= 0 or not self.started_utc:
            raise ValueError("process identity requires guid, positive pid, and start time")


@dataclass(frozen=True)
class Evidence:
    event_id: str
    experiment_id: str
    timestamp_utc: str
    plane: str
    kind: str
    source: ProcessIdentity | None = None
    target_host: str | None = None
    attributes: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(cls, **values: Any) -> "Evidence":
        attributes = values.pop("attributes", {})
        return cls(attributes=tuple(sorted((str(k), str(v)) for k, v in attributes.items())), **values)


@dataclass(frozen=True)
class Decision:
    verdict: Verdict
    reason_codes: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    telemetry_planes: tuple[str, ...]
    explanation: str


@dataclass
class EvidenceGraph:
    _events: dict[str, Evidence] = field(default_factory=dict)

    def add(self, event: Evidence) -> None:
        prior = self._events.get(event.event_id)
        if prior is not None and prior != event:
            raise ValueError("event id collision contains contradictory evidence")
        self._events[event.event_id] = event

    def ordered(self) -> tuple[Evidence, ...]:
        return tuple(sorted(self._events.values(), key=lambda event: (event.timestamp_utc, event.event_id)))
