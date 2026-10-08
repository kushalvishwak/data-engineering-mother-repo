# Sources and attribution

Every question in `nodes/` traces back to one of three public question banks. Raw copies live in
`_sources/` so the vault works offline and any answer can be checked against what the bank
actually said. The nodes are original writing — merged, deduplicated, re-phrased, and corrected
where the source was wrong (see `_meta/BUILD_LOG.md` for the full list of corrections).

| Source | Upstream | Licence | Mirrored as |
|---|---|---|---|
| OBenner — data-engineering-interview-questions | <https://github.com/OBenner/data-engineering-interview-questions> | **No licence file.** All rights reserved by the author by default. | `_sources/obenner/*.md` (38 files, verbatim) |
| Devinterview-io — data-engineer-interview-questions | <https://github.com/Devinterview-io/data-engineer-interview-questions> | **No licence file.** All rights reserved by the author by default. | `_sources/devinterview.md` (the 15 questions the README publishes, verbatim) |
| andkret — Cookbook §08 Interview Questions | <https://github.com/andkret/Cookbook> | Apache-2.0 | `_sources/cookbook_interview.md` |

## Notes

- **Two of the three carry no licence.** They are public repositories, but public is not the same
  as freely redistributable — without a licence, the default is all rights reserved. The mirrors
  are kept here for offline study and traceability, not to republish the banks. If an author
  objects, `_sources/obenner/` and `_sources/devinterview.md` come out and the node files stand on
  their own.
- **`_sources/devinterview_titles.md` reproduces no answers.** That source publishes 15 of its
  advertised 100 questions on GitHub; the remaining 85 sit behind a paywall on devinterview.io.
  The file lists the *titles* of items 1–69 in normalised phrasing and maps each to the node here
  that answers it. Answers were not taken from the gated pages.
- **`_sources/obenner/full.md` was skipped** as a duplicate concatenation of the topic files.
  `delta.md`, `dynamodb.md` and `parquet.md` are 92-byte stubs upstream.

## Apache-2.0 notice, for the Cookbook material

```
Copyright andreaskretz (andkret/Cookbook contributors)
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
```
