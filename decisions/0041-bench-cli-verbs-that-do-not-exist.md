# 0041. Bench CLI verbs that do not exist
**Status:** accepted
**Date:** 2026-10-06
**Affects:** frappe-offline, frappe-bench

## Context

Repeated failures from agents and workers invoking Bench commands that do not exist.

These three wrong verbs appeared often enough to be worth pinning. They read plausibly,
which is exactly why they keep being guessed.

## Decision

The real verbs are:

| Do not use | Use instead |
|---|---|
| `bench switch-to-version` | `bench switch-to-branch <branch>` |
| `bench run-app` | `bench start` |
| `bench run-app` | `bench set-config site developer_mode 1` |
| `bench run_tests` | `bench run-tests --app <app>` |

## Consequences

One more place to look up. `bench --help` is authoritative and should win over this post
if they ever disagree.
