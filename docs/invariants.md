# Security invariants

- **EPR-001:** no target outside the manifest.
- **EPR-002:** removing evidence cannot increase trust.
- **EPR-003:** missing required evidence is `INCOMPLETE` or `NOT_EVALUABLE`, never `BENIGN`.
- **EPR-004:** PID alone is not process identity; `ProcessGuid` and start time delimit a lifetime.
- **EPR-005:** duplicate event identifiers do not increase confidence.
- **EPR-006:** supported event reordering preserves attribution.
- **EPR-007:** names and trust labels cannot override contradictory behavior.
- **EPR-008:** every nontrivial verdict identifies its telemetry planes and evidence.
- **EPR-009:** a network alert alone is not exploit proof.
- **EPR-010:** active execution requires current isolation validation.
- **EPR-011:** synthetic credentials reside only below declared fixture roots.
- **EPR-012:** lateral movement is limited to approved VM pairs.
- **EPR-013:** persistence remains incomplete until cleanup is verified.
- **EPR-014:** attempted access to a non-lab credential source aborts the experiment.
