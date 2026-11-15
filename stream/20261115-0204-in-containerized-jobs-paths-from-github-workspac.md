---
id: 20261115-0204-in-containerized-jobs-paths-from-github-workspac
title: In containerized jobs: paths from GITHUB_WORKSPACE, tools from the image — never host-shaped expansions
kind: lesson
topics: [ci, github-actions, containers, deploy]
projects: [njeremoto-operations]
origin: gift
posted: 2026-11-15T02:04+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Containerizing the deploy job (Pulumi over SSH to a droplet) surfaced two host assumptions in sequence: `actions/setup-dotnet` trying to write the SDK into `/usr/share/dotnet` (root-only, no passwordless sudo on the runner), and then `${{ github.workspace }}` expanding to the **host** path (`/home/gift/actions-runner/_work/...`) inside env and run steps — a path that does not exist in the container, where the workspace mounts at `/__w/...`. The second one survived months unnoticed because the job always ran on the host until the migration day.

## What we decided

In a containerized job, any path must come from `$GITHUB_WORKSPACE` resolved at run time, never from `${{ github.workspace }}` baked into env or scripts; and any tool the job needs at system level comes from the image, not from `setup-*` actions that write to system directories.

## Why

`${{ }}` expressions expand on the runner host before the container exists, so the path is host-shaped; `GITHUB_WORKSPACE` is runner-provided and correct on both sides. The `setup-*` actions assume a GitHub-hosted VM where the runner user has sudo — on a self-hosted box without it, they fail the moment their tool cache is cold. An image that already carries the toolchain makes the whole class moot: the deploy job now runs the same container as ci.yml.

## The cost

`deploy.yml` has no pull_request trigger, so containerization changes to it are validated only by the next master deploy — each wrong assumption costs one failed production deploy cycle (idempotent, so no damage, but ~30 minutes of wall clock). Worth budgeting two iterations for any deploy migration like this.
