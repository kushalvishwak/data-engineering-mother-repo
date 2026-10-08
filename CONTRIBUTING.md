# Contributing

This repository contains source snapshots of projects authored by others. Keep source provenance visible, preserve license files and copyright notices, and do not imply that upstream code or documentation is original to this repository.

## Collection changes

1. Update [SOURCES.md](SOURCES.md) when a URL, pinned revision, license status, or representation changes.
2. Do not redistribute files from projects without a detected license unless explicit permission from the copyright holder has been obtained and recorded.
3. For permitted snapshots, preserve the complete upstream license and notice files. Review nested or third-party content independently.
4. Do not copy secrets or environment-specific configuration; use upstream `.env.example` files where provided.
5. Treat imported snapshots as upstream-owned content. Submit improvements upstream unless the permission terms allow maintaining a derivative here.
6. Keep root-level documentation limited to collection navigation, provenance, and contribution policy.

## Verify source and large files

```powershell
git lfs install
git lfs pull
```

There is no unified build or test command: each source snapshot has its own runtime, dependencies, checks, and license terms. Consult that project's own instructions before running its code.
