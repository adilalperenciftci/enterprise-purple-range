# Media and tool provenance

VM media and executables are retained outside Git under the operator's download directory.

| Item | Source | Observed identity | Local SHA-256 / verification |
|---|---|---|---|
| Windows Server 2025 Evaluation x64 en-US | Microsoft Evaluation Center redirect `https://aka.ms/WinServ2025iso-enus` | build 26100.32230, Standard Evaluation Desktop Experience, 8,152,356,864 bytes | `7B052573BA7894C9924E3E87BA732CCD354D18CB75A883EFA9B900EA125BFD51`; local digest records the downloaded object, not an independently published Microsoft digest |
| Windows 11 Enterprise Evaluation 25H2 x64 en-US | Microsoft Evaluation Center redirect `https://aka.ms/Win11E-ISO-25H2-en-us` | build 26200.6584, Enterprise Evaluation, 7,092,807,680 bytes | `A61ADEAB895EF5A4DB436E0A7011C92A2FF17BB0357F58B13BBC4062E535E7B9`; matched Microsoft's `Win11-Hash-PDF` |
| Sysmon64 | `https://download.sysinternals.com/files/Sysmon.zip` | version 15.22 | `83D31F2478DC6716CFDBF69E5C384BF043072B5F0D8D7B2EEA365F709FDA4352`; valid Microsoft Windows Publisher Authenticode signature |
| Atomic Red Team definitions | `https://github.com/redcanaryco/atomic-red-team` | commit `388942adbd9641f4dfdcf079d7efe9a75ec0ac43` | Git commit pin; only seven YAML definitions were checked out for review |

VirtualBox 7.2.16's generated BIOS answer file omitted the `ModifyPartitions` formatting block for the tested Server ISO. `provision-dc01.ps1` inserts a single active NTFS partition declaration before first boot and resets the boot order after unattended preparation. The workaround is constrained to the generated answer file and fails if its expected insertion point is absent.
