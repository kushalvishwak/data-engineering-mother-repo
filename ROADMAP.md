# Repository collection maintenance roadmap

This repository is a collection of independently authored upstream projects. The numbered folders follow the PDF list, not a unified course or tested technology sequence.

## Current organization

- [x] List all 20 requested projects in the PDF order.
- [x] Preserve each project's source identity and upstream revision.
- [x] Store seven license-detected projects as file snapshots with their license notices.
- [x] Keep the remaining 13 projects as pinned Git submodules because a repository-level license was not detected.
- [x] Exclude upstream `.env` and `.env.*` runtime configuration files from imported snapshots.
- [ ] Obtain explicit permission or a clear license from the remaining upstream authors before considering a file snapshot for those projects.

## Maintenance

- Review each upstream license, notices, and third-party content before changing a project's representation.
- Keep source URLs, import revisions, license status, and representation current in [SOURCES.md](SOURCES.md).
- Update submodule commits only after reviewing upstream changes.
- Do not combine projects, remove upstream notices, or present external material as original work.
- Keep root-level collection guidance separate from the licenses and contribution practices of individual projects.
