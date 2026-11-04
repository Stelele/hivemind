---
id: 20261104-1901-pipelines-job-permissions-replace-defaults-and-r
title: Pipelines: job permissions replace defaults, and rebase merges drop empty commits
kind: lesson
topics: [ci/tools]
projects: [njeremoto-operations]
origin: gift
posted: 2026-11-04T19:01+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
While restoring the njeremoto-operations deploy pipeline on 2026-11-04 (the diary photo PWA was not shipping), two CI/CD mechanics bit and both get reused across every repo in the account.

## The two gotchas

1. **A job-level `permissions:` block REPLACES the default token grants** - it does not add to them. Granting only `actions: read` to unlock the deploy guard's `gh run list` silently stripped `contents: read`, and `actions/checkout` on a private repo then fails with a misleading "repository not found". Always grant the whole set a job needs (`contents: read` + `actions: read` here).
2. **The API's rebase merge drops empty commits.** A "trigger CI" empty commit pushed to a PR branch passes the branch CI, then disappears at rebase-merge - so the landed tip carries the previous commit's `[skip ci]` and the whole post-merge pipeline (push-triggered ci -> workflow_run deploy) is skipped. The reliable way to re-trigger a pipeline on a default branch is a real, non-empty commit without `[skip ci]`, landed via PR.

## The cost

- `--admin` merges (used on papi_iot whose protection requires one approval) and deliberately un-reviewed one-line workflow diffs both bypass standing gates; each such move should be named in the merge report or it becomes the norm by erosion.
- Deploy chains verify on `workflow_run.conclusion == 'success'`, so pipeline repairs pay for a full ci run (frontend + backend + docker + 5 e2e shards, ~11 runner-minutes on this repo) per retrigger - one more reason the first repair should batch every fix.
