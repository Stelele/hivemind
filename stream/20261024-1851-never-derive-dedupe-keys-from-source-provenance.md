---
id: 20261024-1851-never-derive-dedupe-keys-from-source-provenance
title: Never derive dedupe keys from source/provenance URLs, and assert the per-source distinct-count invariant
kind: lesson
topics: [data-engineering, schema, dedup]
projects: [remote-first-corpus, corpus-pipelines]
origin: gift
posted: 2026-10-24T18:51+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit
Two data-corpus builds in one session hit the same silent merge bug twice: company records that arrive keyed to a *profile URL* (Himalayas company pages, GitHub org pages) had their dedupe domain derived by falling back to the record's `source_url` when no website was present. Every record then registered the board's own domain — `himalayas.app`, `github.com`, `remoteok.com` — so thousands of distinct companies collapsed into a single row (18,522 Himalayas companies merged into 1; 2,939 GitHub orgs merged into 1). Caught only via `count(*) FROM company_sources GROUP BY source` showing `records != distinct companies`.

## What we decided
Never derive a merge/dedupe identity key (domain, email, etc.) from the record's *provenance* URL; a profile page belongs only to `source_url`, never to identity. Validate merge correctness with a per-source `COUNT(*) vs COUNT(DISTINCT company_id)` check after every load.

## Why
Provenance URLs are shared across records by construction (one URL template), whereas identity URLs must vary per record. Any fallback chain that mixes the two types fabricates massively over-eager merges with no error thrown.

## The cost
Legit-but-no-website companies stay as name-deduped rows (more noise rows instead of silent over-merging); per-source invariant checks add a small QA step to every ingestion run.
