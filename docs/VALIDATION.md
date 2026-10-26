# Validation — HalawaCore 0.2.0, 2026-10-26

## Local automated checks

- 86 tests passed on Linux / Python 3.14.8, including the original Linux matrix and new Windows x64 ABI/topology fixtures and desktop self-test.
- One non-failing Starlette/httpx test-client deprecation warning remains.
- JavaScript module syntax checks and Python compilation pass.
- Both Linux source and the bundled Linux executable start the API, discover the actual host topology, apply a CPU mask only to their own disposable child, verify the kernel mask, restore and verify the originals.
- Windows source smoke verification under Wine discovers topology. Missing CPU Set interfaces correctly keep affinity read-only. Wine is not physical Windows 10/11 validation.

## Hardware and evidence limits

Live host topology and reversible affinity were verified locally. Local device details and screenshots are excluded from public source. X3D models and architecture variants are tested through synthetic fixtures, not physical X3D hardware.

Windows fixtures exercise fixed-width native structure sizes, legacy/current cache masks, single/dual L3 domains, different processor groups, malformed records, conflicting cache sizes and virtualized X3D uncertainty. Affinity on Windows multi-group systems or explicit CPU Sets remains disabled rather than assuming it is reversible.

## Browser verification

The renamed local dashboard loads real data. The Arabic product website links to the separate program/download page, labels its chip diagram as illustrative, and uses an interface illustration with no live device data. The website does not attempt to inspect visitor processes. Downloads resolve only from real GitHub release assets; unavailable releases use the release listing.

The native GitHub release workflow separately tests/builds on Windows Server and Ubuntu 22.04. Each downloadable archive includes its executable verification report. CI on a virtual Windows Server runner is distinct from physical Windows 10/11 hardware testing.

Local Linux binaries built on the current Arch/CachyOS host may require that host's glibc. GitHub Linux releases are built on Ubuntu 22.04 and target glibc 2.35+.
