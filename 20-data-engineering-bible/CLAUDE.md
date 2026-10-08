# CLAUDE.md — data engineering interview knowledgebase

## What this repo is

A 48-node linked knowledgebase for data-engineering interview prep, merged from three public
question banks. Built 4 Sep 2026 in one session. Every node is a topic; every node ends with
graph edges to its prerequisites, successors and companions, so the vault opens in Obsidian as a
walkable study graph.

Reader model, because it sets priorities: someone interviewing for data engineering / analyst
roles at banks and large enterprises, who can write queries and design scenarios but stalls when
asked to *recite* a definition under pressure — DELETE vs TRUNCATE vs DROP, star vs snowflake,
what SCD stands for. The vault is therefore built as a recall drill, not a textbook: the
definitions come first, phrased to be said out loud.

## Layout

| Path | What |
|---|---|
| `README.md` | Index: mermaid graphs by tier, six-week plan, start-here list, node inventory |
| `SOURCES.md` | Provenance and licence status of the three upstream question banks |
| `_SPEC.md` | Build contract: canonical node ids, the **edge table**, the file template, the rules every node follows |
| `nodes/*.md` | 48 topic files, 608 KB |
| `_sources/` | Local mirror of all three question banks + a coverage checklist |
| `_meta/BUILD_LOG.md` | How it was built, what was corrected, what is deliberately thin |

## Invariants — keep these true

1. Every node file has exactly these five sections, in this order: `## Say it in one line`,
   `## Must be able to recite`, `## Questions actually asked`, `## Traps`, `## Graph`.
2. Frontmatter always carries `id`, `title`, `tier`, `priority`, `sources`.
3. Node ids come from `_SPEC.md`. Never invent one. Adding a node means adding its row to the
   edge table **and** adding the reciprocal wikilinks in the nodes it connects to.
4. `★` on a question means it appears in **at least two of the three source collections** — not
   two files inside one collection. It is a repeat-probability signal; do not dilute it.
5. Answers are one sentence, two clauses maximum: contrast, then one consequence.
6. If a source is wrong or dated, correct it and say so inline in parentheses. The banks are
   full of rot — see `_meta/BUILD_LOG.md`.
7. No invented questions. Gap-fills are capped at three per node and marked
   `(not in sources, but standard)`.

## Validate after any edit

```bash
# run from the vault root
# all five sections present in every node
for f in nodes/*.md; do for s in "^## Say it in one line" "^## Must be able to recite" \
  "^## Questions actually asked" "^## Traps" "^## Graph"; do
  grep -q "$s" "$f" || echo "$(basename $f) missing ${s#^## }"; done; done
# no dangling wikilinks
grep -oh '\[\[[a-z0-9-]*\]\]' nodes/*.md | tr -d '[]' | sort -u > /tmp/links
ls nodes/ | sed 's/\.md$//' | sort > /tmp/ids
comm -23 /tmp/links /tmp/ids          # must be empty
# no orphans (every node linked from at least one other)
for id in $(ls nodes/ | sed 's/\.md$//'); do
  [ "$(grep -l "\[\[$id\]\]" nodes/*.md | grep -v "nodes/$id.md" | wc -l)" -eq 0 ] \
  && echo "ORPHAN: $id"; done
```

## Current state

48/48 nodes, 1,302 questions with answers, 606 ★, 720 recite bullets, 287 traps. Structure valid,
zero dangling links, zero orphans. Tiers: 13 / 18 / 7 / 5 / 5. Priority: 31 must-know,
17 should-know.

## Deliberately thin, do not "fix" by inventing

- `linux-shell` — the sources carry one Linux question in total. Command surface lives in the
  recite section instead.
- `behavioral-project-story` — not source-derived at all; declared as standard practice.
- Snowflake — absent from all three sources. Its facts sit in `warehouse-engines`.
- `azure-data-stack` — the source bank is mostly the retired 2010 Cloud Services platform. Those
  questions were kept (Indian banks recycle them) with the modern equivalent named in each answer.

## Likely next tasks

- Turn the ★ questions into a spaced-repetition deck (Anki export from `grep -h '^- ★'`).
- Add a `sql-dialects` node if he starts getting engine-specific questions.
- Fill `_sources/devinterview_titles.md` items 70–100 if they ever become retrievable.
