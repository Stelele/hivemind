---
id: 20261006-2253-keep-fixer-prompts-to-8-edits-or-fewer
title: Keep fixer prompts to 8 edits or fewer
kind: lesson
topics: [swarm, agents, prompting]
projects: [opencode-config]
origin: gift
posted: 2026-10-06T22:53+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Fixer agents were hitting step limits on batches of 10 or more edits.

## What we decided

Keep fixer prompts to **8 edits or fewer**, and quote the exact string to replace. Longer
batches exhaust the agent's step budget mid-fix.

## Why

Step budget scales with the number of distinct decisions in the prompt, not the number of
lines. Exact strings remove the re-reading that inflates it.

## The cost

More, smaller dispatches. Batch by concern rather than by file count.
