# Architecture

The intended range uses VirtualBox internal network `epr-isolated` (`10.88.0.0/24`). DC01, WIN11, Kali, and Metasploitable3 receive fixed internal addresses; only a host-only management adapter may coexist during execution. Provisioning adapters are removed before experiments. The runner validates the live VM identity, adapters, literal target, approved pair, and egress policy immediately before a fixed command template is selected.

Normalized evidence enters an in-memory graph keyed by stable event identifiers and lifetime-aware process identities. Correlation is deterministic after timestamp ordering and deduplication. A confirmed execution requires independent endpoint and network planes plus a marker tied to one process lifetime. The design does not treat an IDS alert as exploit proof.
