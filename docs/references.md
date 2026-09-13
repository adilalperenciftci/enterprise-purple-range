# References

- [Microsoft Sysmon](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon): Event 1 supplies `ProcessGuid` and command-line context; Event 3 associates network activity with both PID and `ProcessGuid`. Sysmon timestamps are UTC.
- [Windows Event Forwarding for intrusion detection](https://learn.microsoft.com/en-us/windows/security/operating-system-security/device-management/use-windows-event-forwarding-to-assist-in-intrusion-detection): WEF forwards selected operational and administrative events to Windows Event Collector and can retain a reconnecting source backlog.
- [Windows Server 2025 Evaluation Center](https://www.microsoft.com/en-us/evalcenter/download-windows-server-2025): official 180-day evaluation media; activation is required within ten days.
- [Windows 11 Enterprise Evaluation Center](https://www.microsoft.com/en-us/evalcenter/evaluate-windows-11-enterprise): official 90-day Windows 11 Enterprise 25H2 evaluation media.
- [AD DS configuration wizard](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/deploy/ad-ds-installation-and-removal-wizard-page-descriptions): Windows Server 2025 supports creating a new forest; the first controller supplies DNS and the global catalog, and DSRM requires a separate strong secret.
- [Atomic Red Team getting started](https://github.com/redcanaryco/atomic-red-team/wiki/Getting-started): tests are technique-scoped definitions with explicit prerequisites and cleanup; this project selects only reviewed tests and does not install the full payload collection.
