# Repository collection maintenance roadmap

This repository is a collection of independently authored upstream projects. The numbered folders follow the PDF list, not a unified course or tested technology sequence.

## Current organization

- [x] List all 20 requested projects in the PDF order.
- [x] Preserve each project's source identity and upstream revision.
- [x] Store seven license-detected projects as file snapshots with their license notices.
- [x] Materialize all 20 pinned source repositories in root-level folders.
- [x] Record the repository owner's report of permission for the 13 repositories with no detected public license.
- [x] Store the source CSV larger than GitHub's per-file limit via Git LFS.
- [x] Exclude upstream `.env` and `.env.*` runtime configuration files from imported snapshots.

## Maintenance

- Review each upstream license, notices, permission scope, and third-party content before changing a project's representation.
- Keep source URLs, import revisions, license status, and permission notes current in [SOURCES.md](SOURCES.md).
- Update source snapshots only after reviewing upstream changes and applicable permissions.
- Do not combine projects, remove upstream notices, or present external material as original work.
- Keep root-level collection guidance separate from the licenses and contribution practices of individual projects.
