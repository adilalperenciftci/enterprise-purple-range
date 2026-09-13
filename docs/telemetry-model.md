# Telemetry model

Canonical events are bounded NDJSON records. Unknown fields, invalid UTC timestamps, NULs, oversized lines, malformed process identity, and contradictory duplicate identifiers are rejected. A process identity is `(host, ProcessGuid, PID, start UTC)`; PID alone cannot join observations.

Planes are `endpoint`, `identity`, `network`, and `control`. Attributes contain identifiers and metadata required for correlation, never secret values. Raw EVTX, ETL, PCAP, keys, and passwords remain outside Git. Evidence loss is represented by an absent required plane and results in `INCOMPLETE`; malformed evidence results in `NOT_EVALUABLE`.
