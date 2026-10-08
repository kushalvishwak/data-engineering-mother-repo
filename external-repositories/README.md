# External reference repositories

This directory contains the 20 upstream projects listed in the supplied PDF as separate Git submodules. They are pinned to specific upstream commits, shallow-cloned for size, and kept separate from this repository's original lessons.

See [the PDF crosswalk](../19-resources/reference-repositories.md) for each repository's source URL and related curriculum area.

## Initialize and update

Clone the mother repository with its references:

```powershell
git clone --recurse-submodules <mother-repository-url>
```

For an existing clone:

```powershell
git submodule update --init --recursive
```

To update submodules intentionally, review the upstream changes and license terms, then run:

```powershell
git submodule update --remote --recursive
```

The parent repository records each checked-out commit, not a floating branch. Commit updated submodule pointers only after reviewing them.

## License boundary

Each submodule is governed by its upstream repository's license and notices. Inclusion here is for reference and discovery; it does not grant permission to copy, modify, or redistribute the submodule's contents. Check the license in each checkout before reuse.
