# Enterprise Purple Range

This repository correlates endpoint, identity, and network evidence produced by an isolated Active Directory purple-team range. Active execution is restricted to literal addresses and source/target pairs in a versioned manifest. Missing evidence produces `INCOMPLETE` or `NOT_EVALUABLE`, never an implicit clean result.

The current implementation contains the authorization boundary and deterministic in-memory evidence graph. Windows Server and Windows 11 evaluation media are not bundled. Experimental claims are added only after execution evidence is reproduced.

## Local verification

```text
python -m unittest discover -s tests -v
python -m compileall -q avr tests
```

Raw captures, Windows event logs, VM media, disks, snapshots, keys, and lab passwords are excluded from Git.
