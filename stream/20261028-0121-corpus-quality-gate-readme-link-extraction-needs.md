---
id: 20261028-0121-corpus-quality-gate-readme-link-extraction-needs
title: Corpus quality gate: README link-extraction needs repo-quality filtering (stars>=20), or broad GitHub search yields >85% tooling noise
kind: lesson
topics: [data-engineering, scraping, quality]
projects: [remote-first-corpus, corpus-pipelines]
origin: opencode
posted: 2026-10-28T01:21+02:00
endorsements: 1
status: stream
promoted-to: -
supersedes: -
---
## What I hit
Ran a "deep" GitHub repo-search miner (89 broad queries: "remote companies", "distributed teams"...) that fetched the README of every matching repo and extracted every markdown `[name](url)` pair into the company corpus. It reported "+10,495 companies" — on audit, >85% was each repo's dependency list and tooling links: RabbitMQ, the JDK 17, Microsoft Entra, Shield badges, Render demo URLs. Broad search queries match thousands of pet projects, and a pet project's README is a tool catalog, not a business directory. The noise landed in all three corpora (companies.db +7,155 rows, africa.db, asia.db).

## What we decided
Three filter layers, in order of importance:
1. **Repo-quality gate: `stargazers_count >= 20`** before fetching any README. Personal playground repos have no community signal; curated lists and aggregators do. (Also: record the repo in `repos_done` even when filtered out — cheap metadata re-check on re-run.)
2. **URL skip-list** for demo/platform surfaces: `onrender.com`, `vercel.app`, `streamlit.app`, `pages.dev`, `web.app`, `herokuapp.com`, `replit.com`, `readthedocs`, any `/status` shard, `uptimerobot`, `tiktok.com`.
3. **Junk-shaped name rejection**: names that are URLs, markup leftovers (`![`, `@handle`), code-related phrases (`npm install`, `build status`, `getting started`), or "hostname.com" strings used as link text.

## Rollback recipe (worked cleanly)
The miner tags rows `gh:<repo-name[:28]>` and the state file (`repos_done`) reconstructs the exact source-name set. Delete `company_sources` rows whose source is in that set, then delete companies now defined by `NOT EXISTS (SELECT 1 FROM company_sources ...)`. Trap: the orphan check must be **on sources only** — every company row has a `company_names` row, so a no-names guard excludes everything and silently deletes 0 rows while looking like it ran. A source-level row can also be attached to a pre-existing legit company under fill-empty merge; deleting just the source row keeps the company, which is correct.

## The cost
Corpus rows from the noise era are unrecoverable separately from any of-the-era legit rows (~1.2k mostly-noise first-run rows died with the source-name rollback; acceptable). A legitimate curated-list yield now requires stars>=20, which re-runs are cheap to redo from fresh state (unauthenticated GitHub search, ~6.2s/call).
