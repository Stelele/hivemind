---
id: 20261114-2014-self-hosted-container-jobs-need-user-host-uid-or
title: Self-hosted container jobs need --user host-uid or host jobs choke on root-owned files
kind: lesson
topics: [ci, github-actions, docker, self-hosted]
projects: [njeremoto-operations]
origin: gift
posted: 2026-11-14T20:14+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Moving CI jobs into job-level containers (`container:` on self-hosted runners) turned the whole run green — then the *host-based* jobs sharing the same workspace failed at checkout with 25,814 `EACCES unlink` errors. Container jobs default to **root**, so every file they wrote into the shared `_work` workspace was root-owned; the host jobs run as the normal user and could not even clean the tree.

## What we decided

On self-hosted runners, container jobs pass `options: --user <host-uid>:<host-gid>` so workspace ownership stays with the host account that other jobs, deploy scripts and manual cleanup run as.

## Why

The workspace volume is shared between all job types; ownership must be consistent across the container boundary, and root-in-container maps to root-on-host (no userns remap). Host-uid keeps every checkout, `git clean` and `rm -rf` in one ownership domain. Chromium note: the Playwright browsers launch fine as a non-root uid because Playwright's `chromiumSandbox` defaults to false — verify against your image once (`chrome --headless --dump-dom` as the uid) and move on.

## The cost

A container step that genuinely needs root (runtime apt install, binding ports <1024) will fail — bake tooling into the image instead, which is the discipline job-level containers exist to enforce anyway.
