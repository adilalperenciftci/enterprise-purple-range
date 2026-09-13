# Enterprise Purple Range

This repository correlates endpoint, identity, and network evidence produced by an isolated Active Directory purple-team range. Active execution is restricted to literal addresses and source/target pairs in a versioned manifest. Missing evidence produces `INCOMPLETE` or `NOT_EVALUABLE`, never an implicit clean result.

The current implementation contains the authorization boundary, strict event normalization, deterministic in-memory evidence graph, and fixed-command experiment runner. `DC01` hosts the isolated `LAB.AVR.LOCAL` forest; `WIN11` is domain joined and records Sysmon, process-audit, and PowerShell telemetry. `EXP-011` has been reproduced with independent Sysmon and VirtualBox PCAP evidence, while `BENIGN-001` verifies that a local identity query does not trigger the correlation. Other catalog entries remain `NOT_TESTED`. Windows media and raw captures are not bundled.

## Local verification

```text
python -m unittest discover -s tests -v
python -m compileall -q avr tests
```

Raw captures, Windows event logs, VM media, disks, snapshots, keys, and lab passwords are excluded from Git.
