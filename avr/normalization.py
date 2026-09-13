from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Iterable

from .evidence import Evidence, EvidenceGraph, ProcessIdentity


MAX_LINE_BYTES = 65_536
FIELDS = {
    "event_id", "experiment_id", "timestamp_utc", "plane", "kind", "source",
    "target_host", "attributes",
}
PROCESS_FIELDS = {"host", "process_guid", "pid", "started_utc"}
PLANES = {"endpoint", "identity", "network", "control"}


class NormalizationError(ValueError):
    pass


def _utc(value: Any) -> str:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise NormalizationError("timestamp must be an ISO-8601 UTC string")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise NormalizationError("invalid timestamp") from exc
    return value


def _text(value: Any, name: str, limit: int = 512) -> str:
    if not isinstance(value, str) or not value or len(value) > limit or "\x00" in value:
        raise NormalizationError(f"invalid {name}")
    return value


def parse_line(line: str) -> Evidence:
    if len(line.encode("utf-8")) > MAX_LINE_BYTES:
        raise NormalizationError("event exceeds the line limit")
    try:
        raw = json.loads(line)
    except json.JSONDecodeError as exc:
        raise NormalizationError("malformed JSON") from exc
    if not isinstance(raw, dict) or set(raw) - FIELDS:
        raise NormalizationError("event contains unknown fields")
    required = {"event_id", "experiment_id", "timestamp_utc", "plane", "kind"}
    if not required.issubset(raw):
        raise NormalizationError("event is missing required fields")
    plane = _text(raw["plane"], "plane", 32)
    if plane not in PLANES:
        raise NormalizationError("unknown telemetry plane")
    source = None
    if raw.get("source") is not None:
        process = raw["source"]
        if not isinstance(process, dict) or set(process) != PROCESS_FIELDS:
            raise NormalizationError("invalid process identity fields")
        if type(process["pid"]) is not int:
            raise NormalizationError("process pid must be an integer")
        try:
            source = ProcessIdentity(
                _text(process["host"], "process host", 64),
                _text(process["process_guid"], "process guid", 128),
                process["pid"],
                _utc(process["started_utc"]),
            )
        except (TypeError, ValueError) as exc:
            raise NormalizationError("invalid process identity") from exc
    attributes = raw.get("attributes", {})
    if not isinstance(attributes, dict) or len(attributes) > 64:
        raise NormalizationError("invalid attributes")
    safe_attributes = {
        _text(key, "attribute key", 64): _text(value, "attribute value", 2048)
        for key, value in attributes.items()
    }
    target_host = raw.get("target_host")
    if target_host is not None:
        target_host = _text(target_host, "target host", 64)
    return Evidence.create(
        event_id=_text(raw["event_id"], "event id", 128),
        experiment_id=_text(raw["experiment_id"], "experiment id", 64),
        timestamp_utc=_utc(raw["timestamp_utc"]),
        plane=plane,
        kind=_text(raw["kind"], "kind", 64),
        source=source,
        target_host=target_host,
        attributes=safe_attributes,
    )


def load_lines(lines: Iterable[str]) -> EvidenceGraph:
    graph = EvidenceGraph()
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            graph.add(parse_line(line))
        except (NormalizationError, ValueError) as exc:
            raise NormalizationError(f"line {number}: {exc}") from exc
    return graph
