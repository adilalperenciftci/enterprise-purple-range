from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .correlation import evaluate
from .normalization import load_lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("experiment_id")
    parser.add_argument("--profile", default="process_network_marker")
    args = parser.parse_args()
    with args.evidence.open(encoding="utf-8") as stream:
        decision = evaluate(load_lines(stream), args.experiment_id, args.profile)
    print(json.dumps(asdict(decision), separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
