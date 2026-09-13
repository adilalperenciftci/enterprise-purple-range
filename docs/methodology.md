# Methodology

Each experiment is selected from a fixed catalog and executed only after literal target, approved pair, VM identity, adapter topology, and egress checks pass. Evidence is captured before cleanup, hashed outside Git, normalized, deduplicated, ordered, correlated, and compared with a benign fixture. A network alert is supporting evidence, not proof of exploitation.

Claim states are `BENIGN`, `SUSPICIOUS`, `CONFIRMED_ATTACK`, `INCOMPLETE`, and `NOT_EVALUABLE`. `CONFIRMED_ATTACK` requires the exact independent telemetry planes and join key declared by its correlation profile. Experiments remain `NOT_TESTED` until run; scanner output alone does not establish exploitability.
