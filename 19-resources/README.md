# 19 · Resources and references

Use this area for decision aids, primary-documentation pointers, and traceable curriculum references—not as a substitute for the hands-on explanations and implementations elsewhere in the repository.

## Reference policy

- [reference-repositories.md](reference-repositories.md) indexes the 20 GitHub repositories named in the supplied PDF and maps their broad subject areas to this original curriculum.
- The mapping is a starting point rather than an endorsement, content summary, or license audit.
- The upstream projects are separate Git submodules in `external-repositories/`, pinned to commits. Their source remains in independent checkouts rather than being merged into the original learning material.
- A submodule checkout or public link is not a license grant. Review the upstream license and attribution obligations before reusing or redistributing any material.
- To initialize the references after cloning the mother repository, run `git submodule update --init --recursive`; new clones can use `git clone --recurse-submodules <mother-repository-url>`.
- Prefer current official product documentation for behavior that depends on cloud, warehouse, or runtime version. Record product, feature, version/edition, and review date when documenting such behavior.
- Avoid unsupported universal claims about performance, delivery guarantees, or pricing.

## Decision record template

[docs/decision-record-template.md](docs/decision-record-template.md) provides a lightweight template for recording context, options, decision, consequences, and revisit triggers.
