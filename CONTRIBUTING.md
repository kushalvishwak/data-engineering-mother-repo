# Contributing

This repository primarily indexes and organizes work authored by others. Keep source provenance visible, preserve license files and copyright notices, and do not imply that upstream code or documentation is original to this repository.

## Collection changes

1. Update [SOURCES.md](SOURCES.md) when a URL, pinned revision, license status, or representation changes.
2. Keep unlicensed or license-unclear repositories as Git submodules unless the copyright holder grants permission or a clear compatible license is added upstream.
3. For permitted snapshots, preserve the complete upstream license and notice files. Review nested or third-party content independently.
4. Do not copy secrets or environment-specific configuration; use upstream `.env.example` files where provided.
5. Do not modify files inside a submodule as though they were parent-repository files. Submit changes upstream or maintain a properly licensed fork.
6. Keep root-level documentation limited to collection navigation, provenance, and contribution policy.

## Verify submodules

```powershell
git submodule status
git submodule update --init --recursive
```

There is no unified build or test command: each source snapshot and submodule has its own runtime, dependencies, checks, and license terms. Consult that project's own instructions before running its code.
