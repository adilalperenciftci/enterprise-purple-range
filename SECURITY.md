# Security policy

Run active experiments only against project-owned systems listed in `range/manifest.json`. The runner must reject hostnames, CIDRs, target lists, unapproved host pairs, and credential paths outside the synthetic roots. Do not report vulnerabilities in the deliberately vulnerable fixtures as product vulnerabilities.

Report defects that permit range escape, access to non-lab credentials, evidence confusion, or an incorrect benign verdict through a private GitHub security advisory after publication.
