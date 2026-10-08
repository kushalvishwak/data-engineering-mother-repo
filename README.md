# Data Engineering Repository Collection

This repository organizes the 20 GitHub projects listed in the supplied Data Engineer PDF as clearly named folders. Each project retains its source identity; this repository does not claim authorship of upstream work.

## Repository layout

| # | Project | Local directory | Representation |
|---:|---|---|---|
| 1 | Data Engineering Zoomcamp | `01-data-engineering-zoomcamp/` | Git submodule |
| 2 | Data Engineer Handbook | `02-data-engineer-handbook/` | Git submodule |
| 3 | Engineering Cookbook | `03-Cookbook/` | Source snapshot; Apache-2.0 |
| 4 | Engineering Practice | `04-data-engineering-practice/` | Git submodule |
| 5 | Beginner Engineering Code | `05-data_engineering_for_beginners_code/` | Git submodule |
| 6 | Spark Processing Course | `06-efficient_data_processing_spark/` | Git submodule |
| 7 | Awesome Data Engineering | `07-awesome-data-engineering/` | Source snapshot; CC0-1.0 |
| 8 | Engineering Master Roadmap | `08-data-engineering-roadmap/` | Git submodule |
| 9 | Engineer Learning Roadmap | `09-data_engineer_roadmap/` | Git submodule |
| 10 | Engineering Project Lab | `10-data-engineering-projects/` | Source snapshot; MIT |
| 11 | Engineering Project Portfolio | `11-Data-Engineering-Projects/` | Git submodule |
| 12 | Realtime Pipeline Project | `12-e2e-data-engineering/` | Git submodule |
| 13 | Engineering System Design | `13-data-engineering-system-design/` | Source snapshot; MIT |
| 14 | Engineering Interview Questions | `14-OBenner-data-engineering-interview-questions/` | Git submodule |
| 15 | Engineering Interview Practice | `15-dataskew-data-engineering-interview-questions/` | Source snapshot; MIT |
| 16 | Data Engineering Bootcamp | `16-data-engineering-bootcamp/` | Source snapshot; CC0-1.0 |
| 17 | Production Engineering Roadmap | `17-data-engineer-roadmap/` | Git submodule |
| 18 | Pipeline Engineering Project | `18-DataEngineeringProject/` | Source snapshot; MIT |
| 19 | End-to-End Engineering | `19-ritesh-ojha-data-engineering/` | Git submodule |
| 20 | Data Engineering Bible | `20-data-engineering-bible/` | Git submodule |

Source URLs, pinned revisions, and license/representation details are in [SOURCES.md](SOURCES.md).

## Why some projects are submodules

Seven repositories have a detected license that permits redistribution under its terms; their files are present directly in this repository with their upstream license notices preserved. A repository-level license could not be detected for the other 13. Those remain separate Git submodules rather than having their contents copied without a clear grant. This distinction respects the upstream authors and is not a claim that an unlicensed project is public domain.

On GitHub, source snapshots are browsable as ordinary files. A submodule is a pinned link to its upstream repository; its files are not copied into this repository's Git tree. To populate submodule checkouts locally:

```powershell
git clone --recurse-submodules https://github.com/kushalvishwak/data-engineering-mother-repo.git
```

For an existing clone:

```powershell
git submodule update --init --recursive
```

The submodules are pinned to commits. To update them, review the upstream changes and license, then intentionally run `git submodule update --remote --recursive` and commit the updated pointers.

## License and contributions

The root [LICENSE](LICENSE) applies only to original root-level project materials. Every imported source snapshot contains its upstream license notice. Submodule work remains in the upstream repository. Review [SOURCES.md](SOURCES.md) and the relevant upstream license before copying, modifying, or redistributing any project material.

See [CONTRIBUTING.md](CONTRIBUTING.md) before proposing changes.
