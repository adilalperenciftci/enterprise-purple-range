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
