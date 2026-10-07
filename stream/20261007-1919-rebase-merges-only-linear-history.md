---
id: 20261007-1919-rebase-merges-only-linear-history
title: Rebase merges only; linear history
kind: preference
topics: [git, workflow, merging]
projects: [cms-system, personal-site, njeremoto-operations, hivemind, dotfiles]
origin: gift
posted: 2026-10-07T19:19+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Merge commits were accumulating noise in otherwise linear histories.

## What we decided

**Rebase merges only.** Disable merge commits *and* squash; leave rebase enabled.

```
allow_rebase_merge: true
allow_merge_commit: false
allow_squash_merge: false
```

## Why

The repo already commits one logical change per commit (ADR 0006), so rebase preserves
exactly the history you meant to write. Squash would re-flatten those commits and throw
away the boundaries; merge commits add a commit per PR that says nothing.

## The cost

You must keep PR branches tidy — every commit on a PR branch lands on the default
branch as-is. A PR with fixup commits lands as fixup commits. Batching your own
amendments locally before pushing is now part of the workflow.

Squash is off deliberately. If you would rather keep squash available for PRs that
accumulate noisy fixups, say so and this ADR gets superseded.
