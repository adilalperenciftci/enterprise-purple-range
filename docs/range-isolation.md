# Range isolation

The authorized range is the single VirtualBox internal network `epr-isolated`, `10.88.0.0/24`. During active experiments every participating VM must have exactly one enabled adapter attached to that network. NAT, bridged, and host-only adapters are rejected by the runner. Fixed MAC addresses bind manifest identity to the live VM configuration.

Provisioning is separate from execution. Windows media is downloaded from Microsoft outside Git, installation credentials are generated with the operating-system CSPRNG below the ignored `secrets/` directory, and no password is embedded in provisioning code. Any temporary provisioning connectivity must be removed before a snapshot is eligible for experiments.

This validates configuration at a point in time; it does not defend against a hostile hypervisor administrator.

## Verified state

On 2026-09-13, `EPR-DC01` was installed from the recorded Windows Server 2025 Evaluation media, attached only to `epr-isolated`, assigned `10.88.0.10`, and promoted as the domain controller for `LAB.AVR.LOCAL`. The six synthetic accounts declared by the range were queried successfully. VirtualBox snapshot `DC01-FOREST` records that state. This is infrastructure validation, not evidence that any attack experiment has run.

On 2026-09-14, the official Kali Vagrant image was assigned `10.88.0.30` and the official Rapid7 Metasploitable3 Ubuntu image retained `10.88.0.40`. Both addresses are static on `epr-isolated`; all NAT adapters were removed before snapshots `ATTACK-CLEAN` and `TARGET-INSTRUMENTED` were taken. Their fixed MAC addresses match the range manifest. Temporary NAT used for initial key-based provisioning was removed before either image became eligible for experiments.
