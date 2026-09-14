# Validated findings

## EPR-FIND-001 — ProFTPD mod_copy command execution

- Status: CONFIRMED and REPRODUCED
- Experiment: EXP-002
- Target evidence: Nmap identified ProFTPD 1.3.5; the Metasploit module check confirmed unauthenticated `SITE CPFR` support.
- Exploit evidence: a transient command shell opened from META to KALI. The proof commands returned `uid=33(www-data)`, hostname `epr-meta`, and created `/tmp/epr-exp002-marker`.
- Network evidence: the retained-outside-Git capture contains the FTP `CPFR`/`CPTO` sequence, HTTP execution request, and reverse TCP session. Its digest is recorded in the experiment manifest.
- Detection: EPR-NET-001 detects the two security-relevant FTP commands. A normal FTP login/listing baseline does not match; an incomplete stream is `NOT_EVALUABLE`.
- Limits: the network rule establishes exploit-attempt behavior, not successful code execution by itself. Confirmation requires the command output or equivalent target-side evidence.
- Cleanup: Metasploit removed its generated PHP file and closed the command session. After restoring `TARGET-INSTRUMENTED`, an authenticated check confirmed the fixed marker was absent.

## EPR-FIND-002 — Payroll SQL injection

- Status: CONFIRMED and REPRODUCED
- Experiment: EXP-004
- Exploit evidence: an unauthenticated UNION query caused the application to return the fixed `EPR / SYNTHETIC / MARKER / 0` row. No stored payroll data was requested or retained.
- Detection: SID 4208803 and the project evaluator match the endpoint plus URL-encoded `UNION SELECT`. A normal login fixture remains benign and missing HTTP content is not evaluable.
- Limits: this proves query manipulation and authorization-boundary failure, not operating-system command execution.

## Rejected or inconclusive hypotheses

EXP-003 attempts against Samba usermap, UnrealIRCd, and Drupalgeddon2 did not yield a command session. Service banners or a module `check` result are not treated as exploit proof.
