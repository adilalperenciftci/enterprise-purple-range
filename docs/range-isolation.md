# Range isolation

The authorized range is the single VirtualBox internal network `epr-isolated`, `10.88.0.0/24`. During active experiments every participating VM must have exactly one enabled adapter attached to that network. NAT, bridged, and host-only adapters are rejected by the runner. Fixed MAC addresses bind manifest identity to the live VM configuration.

Provisioning is separate from execution. Windows media is downloaded from Microsoft outside Git, installation credentials are generated with the operating-system CSPRNG below the ignored `secrets/` directory, and no password is embedded in provisioning code. Any temporary provisioning connectivity must be removed before a snapshot is eligible for experiments.

This validates configuration at a point in time; it does not defend against a hostile hypervisor administrator.
