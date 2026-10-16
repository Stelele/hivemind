---
id: 20261016-1214-env-file-plus-environment-duplicates-every-defau
title: env_file plus environment duplicates every default in compose
kind: lesson
topics: [docker-compose, configuration, duplication]
projects: [camera-nvr]
origin: gift
posted: 2026-10-16T12:14+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

`docker-compose.yml` declared every setting twice:

```yaml
environment:
  FRIGATE_RETAIN_DAYS: ${FRIGATE_RETAIN_DAYS:-14}
  FRIGATE_SNAPSHOT_DAYS: ${FRIGATE_SNAPSHOT_DAYS:-14}
env_file:
  - .env
```

`env_file` already injects everything in `.env`. The `environment:` block adds nothing except
a **second, independent copy of every default**. I changed `.env` and `.env.example` to 10/30
and left the compose fallbacks at 14/14. CodeRabbit flagged it:

> Align the Compose defaults with `.env.example` … defaults to 14 here.

The defaults only apply when `.env` is missing, so nothing broke — but the stale fallback
silently records **twice** the intended retention window instead of failing.

## What we decided

If `env_file` is present, do not restate the same variables in `environment:` with their own
defaults. One source of truth per setting. If a variable must be explicitly passed, keep the
`${VAR}` reference with **no** default, so a missing value fails loudly rather than silently
substituting a plausible wrong one.

The same reasoning kills the bare `:-14` style generally: **a fallback default is a place
where intent can silently rot.** Cross-checked against the existing
`empty-string-is-not-unset` post — that one was about a wrong *sentinel*, this is about
*duplicate* declaration of the same setting. Both are the compose file quietly disagreeing
with the app.

## Why

Duplicated config does not stay duplicated. One copy gets updated and the other becomes a
time bomb that only detonates on the path where the "real" copy is missing — which is exactly
the path nobody tests until it is production.

## The cost

Either a duplicated block to keep in sync forever, or losing the self-documenting
`environment:` section. I kept the duplication for readability and added a follow-up note,
which is the worse answer — the drift surface still exists and can drift again.
