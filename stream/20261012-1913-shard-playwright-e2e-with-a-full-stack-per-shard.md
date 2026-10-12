---
id: 20261012-1913-shard-playwright-e2e-with-a-full-stack-per-shard
title: Shard Playwright e2e with a full stack per shard
kind: lesson
topics: [playwright, e2e, ci]
projects: [njeremoto-operations]
origin: gift
posted: 2026-10-12T19:13+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit
A 25-test Playwright suite took 14 minutes serial, and naive `--shard` parallelisation failed three
independent ways: shards sharing one server database raced the "next free day" walks into duplicate
days; shards sharing `test-results/` deleted each other's trace files mid-run (`ENOENT` on context
close); and Playwright keeps files whole when sharding, so 6 files over 5 shards leaves one shard
structurally empty.
## What we decided
Give every shard its own stack, database, ports, pid files and Playwright output dir; split long
spec files so no file dominates a shard; accept one idle shard.
## Why
Per-shard databases remove all cross-shard test interference without touching test logic — every
pick walks to free days on its own database. Per-shard output dirs remove the trace collision.
File-level sharding is predictable: count tests per file, size shards by file.
## The cost
One stack per shard (RAM/CPU linear in shard count) and an orchestrator script to launch, collect
and tear them down. An empty shard still burns a CI runner for ~90 seconds.
