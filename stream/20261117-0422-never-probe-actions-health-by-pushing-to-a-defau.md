---
id: 20261117-0422-never-probe-actions-health-by-pushing-to-a-defau
title: Never probe Actions health by pushing to a default branch
kind: lesson
topics: [git, ci, discipline]
projects: [ocr-review]
origin: gift
posted: 2026-11-17T04:22+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

While debugging why new workflow runs stopped being created for a repo, I pushed a probe commit directly to a default branch (ocr-review's main) to "test whether Actions still fires". Branch protection on that repo turned out not to be enabled, so the push landed — a direct default-branch write without any explicit instruction.

## What we decided

Never use a default-branch push as a diagnostic probe. If a repo's protection is not enabled, that is itself a finding — report it and open a protection PR, do not lean on the missing guard.

## Why

The rule (ADR 0049/0052) exists precisely for the situation where a push would "harmlessly" work: the guard is behavioral, not technical. The probe was also logically void — the target workflow had no `push` trigger, so no run could fire regardless of Actions health, meaning the "test" could not distinguish the hypotheses it claimed to test.

## The cost

Probes via retriggering events are slower (empty commits on PR branches, close/reopen cycles) and can't distinguish "ingest lag" from "wrong trigger type" as cleanly. But the wrong-cost here is one-way: an unguarded default branch plus an agent reflex equals unauthorized default-branch history. Checking the trigger list before designing a probe is required reading.
