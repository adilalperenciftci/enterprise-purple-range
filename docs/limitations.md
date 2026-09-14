# Limitations

The range is under construction. Windows/Active Directory infrastructure, restricted enumeration, one ProFTPD exploit, and the `EXP-011` process/network slice are validated. No second exploit, Atomic, credential, persistence, lateral-movement, Zeek, or executed-Suricata result is claimed until corresponding evidence manifests are produced. The current host has approximately 16 GB RAM, so only the VMs required for a given experiment run concurrently.

VirtualBox internal networking establishes a configuration boundary, not protection against a compromised host. Sysmon and Windows event logs are not tamper-proof against a privileged guest attacker. WEF backlog improves collection continuity but does not prove completeness. Clock skew and telemetry loss remain explicit uncertainty inputs.

The VirtualBox 7.2 unattended auxiliary image did not boot under EFI on this host. The Windows 11 evaluation guest therefore uses BIOS firmware with VirtualBox's unattended hardware-check bypass. Endpoint telemetry remains in scope; Secure Boot and EFI-specific behavior are not validated by this range.
