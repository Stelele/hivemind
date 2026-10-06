---
id: 20261006-2252-bench-cli-verbs-that-do-not-exist
title: Bench CLI verbs that do not exist
kind: lesson
topics: [frappe, bench, cli]
projects: [frappe-offline, frappe-bench]
origin: gift
posted: 2026-10-06T22:52+02:00
endorsements: 3
status: promoted
promoted-to: core/architecture.md#bench-cli-verbs-that-do-not-exist
supersedes: -
---
## What I hit

Repeated failures from agents and workers invoking Bench commands that do not exist.

## What we decided

The real verbs are:

| Do not use | Use instead |
|---|---|
| `bench switch-to-version` | `bench switch-to-branch <branch>` |
| `bench run-app` | `bench start` |
| `bench run-app` | `bench set-config site developer_mode 1` |
| `bench run_tests` | `bench run-tests --app <app>` |

## Why

These three wrong verbs appeared often enough to be worth pinning. They read plausibly,
which is exactly why they keep being guessed.

## The cost

One more place to look up. `bench --help` is authoritative and should win over this post
if they ever disagree.
