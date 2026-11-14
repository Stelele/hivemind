---
id: 20261114-0650-core-conflict-flag-adr-0049-0054-baseline-sectio
title: Core conflict flag: ADR 0049/0054 baseline sections still prescribe allow_squash_merge false
kind: question
topics: [workflow, github]
projects: [hivemind]
origin: gift
posted: 2026-11-14T06:50+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

While ratifying ADR 0055 (squash merges enabled account-wide), two LIVE core sections
turned out to still prescribe the old posture: the "Default branch is protected; PR-only,
no force push" section (ADR 0049) and the "Repository baseline" section (ADR 0054) both
contain `allow_squash_merge : false` in their PATCH blocks. An agent following either
section would re-disable squash on a repo, directly contradicting ratified ADR 0055.

Hand-editing core/ is forbidden and no hm command can amend a live section's text, so the
conflict is flagged here rather than fixed in place.

## What we decided

Owner to resolve: either restate the baseline with squash allowed via a corrective
decision post (ratified), or accept ADR 0055 as governing (it is the newest word on merge
methods) and leave the older PATCH snippets as historical text. This post is the flag,
not the fix.

## Why

Core-vs-core conflicts are explicitly routed to the owner per the INDEX header; the two
stale lines are the only known inconsistency created by the 0055-0057 ratification —
ADR 0050's rebase-only rule itself was already superseded citing 0055.

## The cost

- Until resolved, an agent obeying the 0049/0054 PATCH blocks literally would flip
  squash back off on repos it configures, silently undoing ADR 0055's account-wide sweep.
- The stale lines also appear in the hivemind AGENTS.md and ~16 project AGENTS.md files
  ("merges are rebase-only"), which predate the flip and now need a sweep of their own.
