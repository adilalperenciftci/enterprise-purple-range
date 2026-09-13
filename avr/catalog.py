from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .authorization import AuthorizationError, RangeManifest, _unique_object


EXPERIMENT_ID = re.compile(r"EXP-\d{3}\Z")
BASELINE_ID = re.compile(r"BENIGN-\d{3}\Z")
PLANES = {"endpoint", "identity", "network"}


def validate_catalog(path: Path, manifest: RangeManifest) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    experiments = raw.get("experiments")
    baselines = raw.get("baselines")
    if not isinstance(experiments, list) or not isinstance(baselines, list):
        raise AuthorizationError("catalog lists are required")
    ids: set[str] = set()
    for item, pattern in [(item, EXPERIMENT_ID) for item in experiments] + [(item, BASELINE_ID) for item in baselines]:
        if not isinstance(item, dict) or not pattern.fullmatch(item.get("id", "")):
            raise AuthorizationError("invalid catalog entry")
        if item["id"] in ids:
            raise AuthorizationError("duplicate experiment id")
        ids.add(item["id"])
        pair = (item.get("source"), item.get("target"))
        if pair not in manifest.approved_pairs:
            raise AuthorizationError("catalog contains an unauthorized pair")
        if "planes" in item and (not item["planes"] or set(item["planes"]) - PLANES):
            raise AuthorizationError("catalog contains invalid telemetry planes")
    expected = {f"EXP-{number:03d}" for number in range(1, 21)}
    if {item["id"] for item in experiments} != expected or len(baselines) < 6:
        raise AuthorizationError("required experiment coverage is incomplete")
    return raw
