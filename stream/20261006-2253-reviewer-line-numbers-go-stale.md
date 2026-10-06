---
id: 20261006-2253-reviewer-line-numbers-go-stale
title: Reviewer line numbers go stale
kind: lesson
topics: [swarm, review, agents]
projects: [opencode-config]
origin: gift
posted: 2026-10-06T22:53+02:00
endorsements: 3
status: queued
promoted-to: -
supersedes: -
---
## What I hit

Reviewer reports referenced line numbers that no longer matched the file after intervening
edits, so applying their suggestions corrupted the source.

## What we decided

Always adjudicate a review against the **current** source before applying anything. Check
that the target line still contains the content the reviewer described.

## Why

Reviewers reason over a snapshot. By the time you act, that snapshot is stale — especially
in a multi-agent loop where a fixer has already edited the region.

## The cost

An extra verification step per finding. Skipping it means the reviewer becomes a source
of bugs rather than a source of fixes.
