# Coverage matrix

`NOT_TESTED` rows are planned coverage, not successful results.

| Experiment | ATT&CK | Network | Endpoint | Identity | Credential | Persistence | Detection | Benign | Variant | Result |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| EXP-001 | T1046 | yes | no | no | no | no | none | pending | no | REPRODUCED |
| EXP-002 | T1190 | yes | yes | no | no | no | EPR-NET-001 | normal FTP | replayed | CONFIRMED/DETECTED |
| EXP-003 | T1190 | yes | yes | no | no | no | none | pending | attempted | INCONCLUSIVE |
| EXP-004 | T1190 | yes | yes | no | no | no | EPR-NET-001/4208803 | normal login | encoded | CONFIRMED/DETECTED |
| EXP-005 | T1059.001 | no | yes | no | no | no | pending | BENIGN-002 | yes | NOT_TESTED |
| EXP-006 | T1059.003 | no | yes | no | no | no | pending | BENIGN-001 | yes | NOT_TESTED |
| EXP-007 | T1082 | no | yes | no | no | no | pending | BENIGN-001 | no | NOT_TESTED |
| EXP-008 | T1016 | no | yes | no | no | no | pending | BENIGN-001 | no | NOT_TESTED |
| EXP-009 | T1007 | no | yes | no | no | no | pending | BENIGN-001 | no | NOT_TESTED |
| EXP-010 | T1053.005 | no | yes | no | no | yes | pending | BENIGN-002 | no | NOT_TESTED |
| EXP-011 | T1059.001 | yes | yes | no | no | no | EPR-CORR-001 | BENIGN-001 | replayed | REPRODUCED/DETECTED |
| EXP-012 | T1059.001 | no | yes | no | no | no | pending | BENIGN-002 | yes | NOT_TESTED |
| EXP-013 | T1552.001 | no | yes | no | yes | no | pending | BENIGN-002 | yes | NOT_TESTED |
| EXP-014 | T1552.001 | no | yes | no | yes | no | pending | BENIGN-002 | yes | NOT_TESTED |
| EXP-015 | T1053.005 | no | yes | no | no | yes | pending | BENIGN-002 | yes | NOT_TESTED |
| EXP-016 | T1543.003 | no | yes | no | no | yes | pending | BENIGN-002 | yes | NOT_TESTED |
| EXP-017 | T1021.006 | yes | yes | yes | no | no | pending | BENIGN-005 | yes | NOT_TESTED |
| EXP-018 | T1021.006 | yes | yes | yes | yes | no | EPR-CORR-002/003 | BENIGN-005 | yes | NOT_TESTED |
| EXP-019 | T1036 | no | yes | no | no | no | pending | BENIGN-002 | yes | NOT_TESTED |
| EXP-020 | N/A | yes | yes | no | no | no | completeness invariant | BENIGN-006 | loss | NOT_TESTED |
