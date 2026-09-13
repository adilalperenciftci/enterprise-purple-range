# Threat model

The range evaluates deliberately executed behavior by project-owned identities on project-owned VMs. The trusted computing base is the Windows host, VirtualBox, immutable experiment definitions, the live topology check, the telemetry configuration, and the normalization/correlation code.

The range detects or records synthetic credential access, authentication, process execution, internal connections, reversible persistence, and controlled host transitions when the required telemetry planes are available. It fails closed on unknown targets, unauthorized pairs, malformed identity, contradictory duplicate identifiers, and missing required planes.

It does not defend against a hostile host or hypervisor administrator, compromised kernel, disabled telemetry, forged privileged event logs, or attacks outside the isolated network. Administrator-level experiments can affect disposable guests; snapshots and explicit cleanup verification bound that effect. No LSASS, SAM, SECURITY, DPAPI, browser profile, or non-lab credential collection is in scope.
