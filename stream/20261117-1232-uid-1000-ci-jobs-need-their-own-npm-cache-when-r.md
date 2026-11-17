---
id: 20261117-1232-uid-1000-ci-jobs-need-their-own-npm-cache-when-r
title: uid-1000 CI jobs need their own npm cache when root jobs share _github_home
kind: lesson
topics: [ci, self-hosted-runners, npm, github-actions]
projects: [njeremoto-operations]
origin: gift
posted: 2026-11-17T12:32+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

On njeremoto-operations PR #82, CI jobs failed `npm ci` with `EACCES — cache folder contains
root-owned files` at `/github/home/.npm/_cacache`. Which jobs failed changed every run (three
e2e shards, then the frontend unit job) — a scheduling lottery, not a code failure. Moving the
polluted cache aside while the runner was idle did not hold: a concurrent root-running job
(the OCR review container, whose `.opencodereview` dir in the same volume is root-owned)
re-polluted the fresh cache within three minutes.

## What we decided

On self-hosted runners where root container jobs and uid-1000 container jobs share
`_work/_temp/_github_home`, give the uid-1000 jobs their own npm cache via job-level
`env: npm_config_cache: /github/home/.npm-uid1000`. Do not bother chowning or moving the
shared cache aside — a concurrent root job re-pollutes it.

## Why

`_github_home` persists across jobs on a runner and is shared by every container job on it,
regardless of user. Root jobs write cache files uid-1000 jobs cannot overwrite, so whichever
job npm-installs after a root job fails. A per-uid cache directory removes the shared
writable surface: no sudo, no change to shared reusable workflows (Stelele/ocr-review runs
as root on 100 repos), no scheduling dependence. njeremoto-operations' ci.yml already ran
its container jobs as `--user 1000:1000` after root leftovers once broke a host checkout
with 25k EACCES errors — this is the same failure class one layer down.

## The cost

A second npm cache directory per runner (disk duplication; cold cache on first use per
runner). The root cause — root and non-root jobs sharing one HOME volume — remains for
every other tool's cache (`~/.cache`, playwright browsers, etc.); this fix covers npm only.
The durable alternative is making the root jobs run as uid 1000 or giving them a separate
HOME, which means touching the shared OCR workflow for all repos.
